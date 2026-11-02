// @ts-nocheck
import { definePlugin, staticClasses, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { callable, addEventListener, removeEventListener, toaster } from "@decky/api";
import { FaBolt } from "react-icons/fa";
import { useState, useEffect } from "react";

const UUMonitorContent = () => {
  const [uiToggleState, setUiToggleState] = useState(false);
  const [realTextState, setRealTextState] = useState(false);

  const [monitorEnabled, setMonitorEnabled] = useState(() => {
    const saved = localStorage.getItem("areuok_monitor_enabled");
    if (saved === null) {
      localStorage.setItem("areuok_monitor_enabled", "true");
      return true;
    }
    return saved === "true";
  });

  const fetchRealStatus = async () => {
    try {
      const checkTunFunc = callable<[], boolean>('check_tun');
      const status = await checkTunFunc();
      setUiToggleState(status);
      setRealTextState(status);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRealStatus();
    const localListener = (isConnected: boolean) => {
      setUiToggleState(isConnected);
      setRealTextState(isConnected);
    };
    addEventListener("uu_status_change", localListener);

    return () => {
      removeEventListener("uu_status_change", localListener);
    };
  }, []);

  const handleToggleClick = () => {
    setUiToggleState((prev) => !prev);
    setTimeout(fetchRealStatus, 200);
  };

  const handleMonitorToggle = async (enabled: boolean) => {
    setMonitorEnabled(enabled);
    localStorage.setItem("areuok_monitor_enabled", enabled.toString());
    try {
      const setBackendStatus = callable<[boolean], void>('set_monitor_enabled');
      await setBackendStatus(enabled);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <PanelSection title="ARE U OK 状态监控">
    <PanelSectionRow>
    <ToggleField
    label="当前加速状态"
    description={realTextState ? "已连接 (TUN 虚拟网卡活跃)" : "未连接"}
    checked={uiToggleState}
    onChange={handleToggleClick}
    />
    </PanelSectionRow>
    <PanelSectionRow>
    <ToggleField
    label="后台状态监听"
    description={monitorEnabled ? "已开启 (状态变化时自动通知)" : "已关闭 (不再后台耗电)"}
    checked={monitorEnabled}
    onChange={handleMonitorToggle}
    />
    </PanelSectionRow>
    </PanelSection>
  );
};

export default definePlugin((serverApi) => {
  console.log("🔥 AreUOK Dev: 插件环境初始化");

  const globalListener = (isConnected: boolean) => {
    toaster.toast({
      title: "Are U OK",
                  body: isConnected ? "加速器已连接" : "加速器已断开",
                  icon: window.SP_REACT.createElement(FaBolt),
    });
  };

  addEventListener("uu_status_change", globalListener);

  // 前端加载完毕，直接读取本地存储并告知后端（不再等谁，直接发）
  let initialEnabled = localStorage.getItem("areuok_monitor_enabled");
  if (initialEnabled === null) {
    initialEnabled = "true";
    localStorage.setItem("areuok_monitor_enabled", "true");
  }
  const setBackendStatus = callable<[boolean], void>('set_monitor_enabled');
  setBackendStatus(initialEnabled === "true").catch(console.error);

  return {
    title: <div className={staticClasses.Title}>ARE U OK</div>,
                            content: <UUMonitorContent />,
                            icon: <FaBolt />,
                            onDismount() {
                              removeEventListener("uu_status_change", globalListener);
                            },
  };
});
