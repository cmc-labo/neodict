"""
自動更新のスケジューラー
"""

import schedule
import time
import logging
from datetime import datetime
from typing import Optional, Callable
from threading import Thread
from .updater import DictUpdater

logger = logging.getLogger(__name__)


class UpdateScheduler:
    """辞書の自動更新をスケジュール"""

    def __init__(self, updater: Optional[DictUpdater] = None):
        """
        初期化

        Args:
            updater: 使用するDictUpdaterインスタンス
        """
        self.updater = updater or DictUpdater()
        self.running = False
        self.thread: Optional[Thread] = None

    def schedule_daily(self, hour: int = 3, minute: int = 0):
        """
        毎日指定時刻に更新をスケジュール

        Args:
            hour: 実行時(0-23)
            minute: 実行分(0-59)
        """
        time_str = f"{hour:02d}:{minute:02d}"

        schedule.every().day.at(time_str).do(self._update_job)

        logger.info(f"Scheduled daily update at {time_str}")

    def schedule_hourly(self, minute: int = 0):
        """
        毎時指定分に更新をスケジュール

        Args:
            minute: 実行分(0-59)
        """
        schedule.every().hour.at(f":{minute:02d}").do(self._update_job)

        logger.info(f"Scheduled hourly update at minute {minute}")

    def schedule_weekly(self, day: str = "monday", hour: int = 3, minute: int = 0):
        """
        毎週指定曜日・時刻に更新をスケジュール

        Args:
            day: 曜日(monday, tuesday, etc.)
            hour: 実行時(0-23)
            minute: 実行分(0-59)
        """
        time_str = f"{hour:02d}:{minute:02d}"

        getattr(schedule.every(), day).at(time_str).do(self._update_job)

        logger.info(f"Scheduled weekly update on {day} at {time_str}")

    def schedule_custom(self, interval_minutes: int):
        """
        カスタム間隔で更新をスケジュール

        Args:
            interval_minutes: 更新間隔(分)
        """
        schedule.every(interval_minutes).minutes.do(self._update_job)

        logger.info(f"Scheduled update every {interval_minutes} minutes")

    def start(self, blocking: bool = False):
        """
        スケジューラーを開始

        Args:
            blocking: ブロッキングモードで実行するか
        """
        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True
        logger.info("Starting scheduler...")

        if blocking:
            self._run_scheduler()
        else:
            self.thread = Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()

    def stop(self):
        """スケジューラーを停止"""
        logger.info("Stopping scheduler...")
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

    def run_now(self) -> Dict:
        """
        即座に更新を実行

        Returns:
            更新結果の統計
        """
        return self._update_job()

    def _run_scheduler(self):
        """スケジューラーのメインループ"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def _update_job(self) -> Dict:
        """更新ジョブを実行"""
        logger.info(f"Running scheduled update at {datetime.now()}")

        try:
            stats = self.updater.update()
            logger.info(f"Update completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error during update: {e}", exc_info=True)
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_next_run(self) -> Optional[datetime]:
        """
        次の実行時刻を取得

        Returns:
            次の実行予定時刻(スケジュールされていない場合はNone)
        """
        jobs = schedule.jobs
        if jobs:
            next_job = min(jobs, key=lambda j: j.next_run)
            return next_job.next_run

        return None
