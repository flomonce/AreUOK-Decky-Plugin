// @ts-nocheck
import { definePlugin, staticClasses, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { callable } from "@decky/api";
import { FaBolt } from "react-icons/fa";
import { useState, useEffect } from "react";

const UUMonitorContent = () => {
  const [uiToggleState, setUiToggleState] = useState(false);
  const [realTextState, setRealTextState] = useState(false);

  const fetchRealStatus = async () => {
    try {
      const checkTunFunc = callable<[], boolean>('check_tun');
      const status = await checkTunFunc();
      setUiToggleState(status);
      setRealTextState(status);
    } catch (e) {
      console.error("callable 调用失败:", e);
      setUiToggleState(false);
      setRealTextState(false);
    }
  };

  useEffect(() => {
    fetchRealStatus();
  }, []);

  const handleToggleClick = () => {
    setUiToggleState((prev) => !prev);
    setTimeout(() => {
      fetchRealStatus();
    }, 200);
  };

  return (
    <PanelSection title="ARE U OK 状态监控">
    <PanelSectionRow>
    <ToggleField
    label="加速状态"
    description={realTextState ? "已连接 (TUN 虚拟网卡活跃)" : "未连接"}
    checked={uiToggleState}
    onChange={handleToggleClick}
    />
    </PanelSectionRow>
    </PanelSection>
  );
};

// 核心：恢复我们之前验证成功的黑科技写法
const plugin_export_var = definePlugin((serverApi) => {
  return {
    title: <div className={staticClasses.Title}>ARE U OK</div>,
    content: <UUMonitorContent />,
    icon: <FaBolt />,
    onDismount() {},
  };
});

export default plugin_export_var;

if (typeof window !== "undefined") {
  window.__DECKY_PLUGIN_EXPORT__ = plugin_export_var;
}
