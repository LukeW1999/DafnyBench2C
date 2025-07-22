"""
Batch processing manager with progress tracking and resume capability
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, asdict
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class BatchItem:
    """Single batch processing item"""
    input_file: str
    output_dir: str
    status: str = "pending"  # pending, running, completed, failed, skipped
    conversion_score: Optional[float] = None
    validation_score: Optional[float] = None
    test_success: Optional[bool] = None
    error_message: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    retry_count: int = 0
    notes: str = ""

class BatchManager:
    """Batch processing manager"""
    
    def __init__(self, batch_name: str, output_dir: Path):
        self.batch_name = batch_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create clear directory structure
        self.results_dir = self.output_dir / "results"
        self.converted_dir = self.output_dir / "converted"
        self.reports_dir = self.output_dir / "reports"
        
        for dir_path in [self.results_dir, self.converted_dir, self.reports_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Progress file path
        self.progress_file = self.reports_dir / f"{batch_name}_progress.json"
        self.summary_file = self.reports_dir / f"{batch_name}_summary.csv"
        
        # Load or initialize progress
        self.items: List[BatchItem] = []
        self.completed_files: Set[str] = set()
        self.load_progress()
    
    def get_output_path_for_file(self, input_file: Path) -> Path:
        """Generate clear output path for a single file"""
        # Use original filename as directory name to avoid long paths
        safe_name = input_file.stem.replace("_tmp_tmp", "_").replace("tmp_", "")
        # Limit length to avoid long paths
        if len(safe_name) > 50:
            safe_name = safe_name[:47] + "..."
        
        return self.converted_dir / safe_name
    
    def add_files(self, input_files: List[Path], output_subdir: str = None):
        """Add files to the batch list"""
        for input_file in input_files:
            output_path = self.get_output_path_for_file(input_file)
            
            item = BatchItem(
                input_file=str(input_file),
                output_dir=str(output_path)
            )
            
            # Check if already processed
            if item.input_file in self.completed_files:
                item.status = "completed"
                logger.info(f"File {input_file.name} already completed, skipping")
            else:
                item.status = "pending"
            
            self.items.append(item)
        
        logger.info(f"Added {len(input_files)} files to batch '{self.batch_name}'")
        self.save_progress()
    
    def get_pending_files(self) -> List[BatchItem]:
        """Get pending files"""
        return [item for item in self.items if item.status == "pending"]
    
    def get_completed_files(self) -> List[BatchItem]:
        """Get completed files"""
        return [item for item in self.items if item.status == "completed"]
    
    def get_failed_files(self) -> List[BatchItem]:
        """Get failed files"""
        return [item for item in self.items if item.status == "failed"]
    
    def mark_running(self, input_file: str):
        """Mark file as running"""
        for item in self.items:
            if item.input_file == input_file:
                item.status = "running"
                item.start_time = datetime.now().isoformat()
                break
        self.save_progress()
    
    def mark_completed(self, input_file: str, conversion_score: float, 
                      validation_score: float, test_success: bool, 
                      error_message: str = None, notes: str = ""):
        """Mark file as completed"""
        for item in self.items:
            if item.input_file == input_file:
                item.status = "completed"
                item.conversion_score = conversion_score
                item.validation_score = validation_score
                item.test_success = test_success
                item.error_message = error_message
                item.notes = notes
                item.end_time = datetime.now().isoformat()
                self.completed_files.add(input_file)
                break
        self.save_progress()
    
    def mark_failed(self, input_file: str, error_message: str, notes: str = ""):
        """Mark file as failed"""
        for item in self.items:
            if item.input_file == input_file:
                item.status = "failed"
                item.error_message = error_message
                item.notes = notes
                item.end_time = datetime.now().isoformat()
                item.retry_count += 1
                break
        self.save_progress()
    
    def mark_skipped(self, input_file: str, reason: str):
        """Mark file as skipped"""
        for item in self.items:
            if item.input_file == input_file:
                item.status = "skipped"
                item.notes = reason
                item.end_time = datetime.now().isoformat()
                break
        self.save_progress()
    
    def reset_failed_files(self):
        """Reset failed files to pending status"""
        for item in self.items:
            if item.status == "failed":
                item.status = "pending"
                item.error_message = None
                item.notes = ""
                item.start_time = None
                item.end_time = None
        self.save_progress()
        logger.info("Reset all failed files to pending status")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        total = len(self.items)
        completed = len(self.get_completed_files())
        failed = len(self.get_failed_files())
        pending = len(self.get_pending_files())
        running = len([item for item in self.items if item.status == "running"])
        skipped = len([item for item in self.items if item.status == "skipped"])
        
        # Calculate average scores
        completed_items = self.get_completed_files()
        avg_conversion_score = 0.0
        avg_validation_score = 0.0
        test_success_rate = 0.0
        
        if completed_items:
            conversion_scores = [item.conversion_score for item in completed_items if item.conversion_score is not None]
            validation_scores = [item.validation_score for item in completed_items if item.validation_score is not None]
            test_successes = [item.test_success for item in completed_items if item.test_success is not None]
            
            avg_conversion_score = sum(conversion_scores) / len(conversion_scores) if conversion_scores else 0.0
            avg_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
            test_success_rate = sum(test_successes) / len(test_successes) if test_successes else 0.0
        
        return {
            "batch_name": self.batch_name,
            "total_files": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "running": running,
            "skipped": skipped,
            "completion_rate": completed / total if total > 0 else 0.0,
            "avg_conversion_score": avg_conversion_score,
            "avg_validation_score": avg_validation_score,
            "test_success_rate": test_success_rate,
            "last_updated": datetime.now().isoformat()
        }
    
    def print_progress(self):
        """Print progress information"""
        summary = self.get_progress_summary()
        
        print(f"\n{'='*60}")
        print(f"📊 Batch Progress: {summary['batch_name']}")
        print(f"{'='*60}")
        print(f"📁 Total Files: {summary['total_files']}")
        print(f"✅ Completed: {summary['completed']} ({summary['completion_rate']*100:.1f}%)")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏳ Pending: {summary['pending']}")
        print(f"🔄 Running: {summary['running']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"📈 Average Validation Score: {summary['avg_validation_score']:.3f}")
        print(f"🧪 Test Success Rate: {summary['test_success_rate']*100:.1f}%")
        print(f"🕒 Last Updated: {summary['last_updated']}")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed Files:")
            for item in self.get_failed_files():
                print(f"  - {Path(item.input_file).name}: {item.error_message}")
        
        print(f"{'='*60}\n")
    
    def save_progress(self):
        """Save progress to file"""
        # Save detailed progress in JSON format
        progress_data = {
            "batch_name": self.batch_name,
            "last_updated": datetime.now().isoformat(),
            "items": [asdict(item) for item in self.items]
        }
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
        
        # Save summary in CSV format
        summary = self.get_progress_summary()
        with open(self.summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in summary.items():
                writer.writerow([key, value])
        
        logger.info(f"Progress saved to {self.progress_file}")
    
    def load_progress(self):
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                
                self.items = [BatchItem(**item_data) for item_data in progress_data.get('items', [])]
                self.completed_files = {item.input_file for item in self.items if item.status == "completed"}
                
                logger.info(f"Loaded progress for batch '{self.batch_name}': {len(self.items)} items")
            except Exception as e:
                logger.error(f"Failed to load progress: {e}")
                self.items = []
                self.completed_files = set()
        else:
            logger.info(f"No existing progress file found, starting fresh batch '{self.batch_name}'")
    
    def export_detailed_results(self, output_file: str = None) -> Path:
        """Export detailed results to CSV"""
        if output_file is None:
            output_file = f"{self.batch_name}_detailed_results.csv"
        
        output_path = self.reports_dir / output_file
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Input_File', 'Status', 'Conversion_Score', 'Validation_Score', 
                'Test_Success', 'Error_Message', 'Start_Time', 'End_Time', 
                'Retry_Count', 'Notes'
            ])
            
            for item in self.items:
                writer.writerow([
                    Path(item.input_file).name,
                    item.status,
                    item.conversion_score or "N/A",
                    item.validation_score or "N/A",
                    item.test_success or "N/A",
                    item.error_message or "N/A",
                    item.start_time or "N/A",
                    item.end_time or "N/A",
                    item.retry_count,
                    item.notes
                ])
        
        logger.info(f"Detailed results exported to {output_path}")
        return output_path
    
    def create_readme(self) -> Path:
        """Create README file explaining output structure"""
        readme_path = self.output_dir / "README.md"
        
        readme_content = f"""# Batch Conversion Results: {self.batch_name}

## 📁 Directory Structure

```
{self.output_dir.name}/
├── converted/           # Converted C code files
│   ├── file1/          # Each Dafny file gets its own directory
│   │   ├── main.c      # Converted C code
│   │   └── test.c      # Generated test file
│   └── file2/
│       ├── main.c
│       └── test.c
├── reports/            # Progress and result reports
│   ├── {self.batch_name}_progress.json    # Detailed progress (JSON format)
│   ├── {self.batch_name}_summary.csv      # Progress summary (CSV format)
│   └── {self.batch_name}_detailed_results.csv  # Detailed results (CSV format)
└── results/            # Other result files
```

## 📊 Progress Summary

- **Total Files**: {len(self.items)}
- **Completed**: {len(self.get_completed_files())}
- **Failed**: {len(self.get_failed_files())}
- **Pending**: {len(self.get_pending_files())}

## 🔍 How to Read Results

1. **converted/**: Each subdirectory contains conversion results for one Dafny file
2. **reports/**: Contains progress tracking and statistics
3. **results/**: Other related result files

## 📈 Validation Scores

- **Conversion Score**: Whether conversion was successful (1.0 = success, 0.0 = failure)
- **Validation Score**: Conversion quality score (0.0-1.0)
- **Test Success**: Whether tests passed (True/False)

## 🚀 Resume Capability

If batch processing is interrupted, you can restart with the same command to continue processing remaining files.
The system will automatically skip already completed files.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"README created at {readme_path}")
        return readme_path 