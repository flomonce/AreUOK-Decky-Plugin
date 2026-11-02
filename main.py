import decky
import subprocess
import asyncio

class Plugin:
    async def _main(self):
        decky.logger.info("====== Are U OK 后端已启动 (V16) ======")
        self.current_tun_status = False
        self.monitor_process = None
        self.monitor_task = None
        self.sleep_watch_task = None

        self.monitor_enabled = False
        self.is_booted = False  # 标记是否已经经历过首次开机启动

        # 休眠唤醒监听常驻
        self.sleep_watch_task = asyncio.create_task(self._watch_sleep_events())

    async def set_monitor_enabled(self, enabled: bool):
        """受前端开关绝对控制"""
        self.monitor_enabled = enabled
        decky.logger.info(f"监控开关状态变更为: {enabled}")

        if enabled:
            if self.monitor_task is None or self.monitor_task.done():
                # 【核心判断】如果不是首次启动（即用户在面板里手动关了又开），就不需要延迟
                apply_delay = not self.is_booted
                self.is_booted = True
                self.monitor_task = asyncio.create_task(
                    self._monitor_tun_events(is_wakeup=False, apply_delay=apply_delay)
                )
        else:
            if self.monitor_task and not self.monitor_task.done():
                self.monitor_task.cancel()
                self.monitor_task = None

    async def check_tun(self) -> bool:
        try:
            res = await asyncio.to_thread(
                subprocess.run,
                ["ip", "link", "show"],
                capture_output=True,
                text=True
            )
            return "tun" in res.stdout and "tunl0" not in res.stdout
        except Exception as e:
            decky.logger.error(f"查网卡报错: {e}")
            return False

    async def _monitor_tun_events(self, is_wakeup=False, apply_delay=False):
        """核心逻辑：查状态 -> (可选延迟) -> 发通知 -> 持续零延迟监听"""

        # 1. 查初始状态
        is_connected = False
        for i in range(5):
            is_connected = await self.check_tun()
            if is_connected:
                break
            await asyncio.sleep(1)

        self.current_tun_status = is_connected

        # 2. 处理开机/唤醒的延迟通知
        if is_connected:
            if apply_delay:
                decky.logger.info(f"开机/唤醒首次检测已连接，延迟 3 秒等待 UI 渲染...")
                await asyncio.sleep(3)
            else:
                decky.logger.info(f"手动开启/重载，立即发送连接通知...")

            # 延迟期间用户可能关掉了开关，再次确认
            if self.monitor_enabled:
                await decky.emit("uu_status_change", True)

        # 3. 进入持续监听循环（此循环内产生的所有状态变化，全部零延迟秒发）
        while True:
            try:
                decky.logger.info("启动 ip monitor link 监听进程...")
                self.monitor_process = await asyncio.create_subprocess_exec(
                    "ip", "monitor", "link",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                while True:
                    line = await self.monitor_process.stdout.readline()
                    if not line:
                        break

                    text = line.decode('utf-8').strip()
                    if "tun" in text and "tunl0" not in text:
                        if ("state UNKNOWN" in text or "state UP" in text) and "Deleted" not in text:
                            if not self.current_tun_status:
                                self.current_tun_status = True
                                # 零延迟立即弹窗
                                await decky.emit("uu_status_change", True)
                        elif "Deleted" in text or "state DOWN" in text:
                            if self.current_tun_status:
                                self.current_tun_status = False
                                # 零延迟立即弹窗
                                await decky.emit("uu_status_change", False)

            except asyncio.CancelledError:
                if self.monitor_process and self.monitor_process.returncode is None:
                    try:
                        self.monitor_process.terminate()
                    except:
                        pass
                break
            except Exception as e:
                decky.logger.error(f"监听崩溃: {e}")
                await asyncio.sleep(5)

    async def _watch_sleep_events(self):
        """纯粹的唤醒监听"""
        while True:
            try:
                process = await asyncio.create_subprocess_exec(
                    "dbus-monitor", "--system", "type='signal',interface='org.freedesktop.login1.Manager',member='PrepareForSleep'",
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    text = line.decode('utf-8').strip()
                    if "boolean false" in text:
                        decky.logger.info("系统唤醒...")
                        if self.monitor_enabled:
                            if self.monitor_task and not self.monitor_task.done():
                                self.monitor_task.cancel()
                                await asyncio.sleep(0.5)
                            # 唤醒必定触发延迟
                            self.monitor_task = asyncio.create_task(
                                self._monitor_tun_events(is_wakeup=True, apply_delay=True)
                            )
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(5)

    async def _unload(self):
        if self.monitor_task:
            self.monitor_task.cancel()
        if self.sleep_watch_task:
            self.sleep_watch_task.cancel()
