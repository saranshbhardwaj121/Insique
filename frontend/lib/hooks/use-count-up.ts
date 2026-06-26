"use client";

import * as React from "react";

export function useCountUp(target: number, duration = 800, enabled = true) {
  const [value, setValue] = React.useState(0);
  const valueRef = React.useRef(0);
  const previousTarget = React.useRef(target);

  React.useEffect(() => {
    if (!enabled) {
      setValue(target);
      valueRef.current = target;
      return;
    }

    const startTime = performance.now();
    const startValue = previousTarget.current !== target ? 0 : valueRef.current;

    let rafId: number;
    const step = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startValue + (target - startValue) * eased);
      valueRef.current = current;
      setValue(current);
      if (progress < 1) {
        rafId = requestAnimationFrame(step);
      }
    };

    previousTarget.current = target;
    rafId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafId);
  }, [target, duration, enabled]);

  return value;
}
