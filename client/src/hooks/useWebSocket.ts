"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import type { WsMessage } from "@/lib/api";

const WS_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ||
    "ws://localhost:8000";

const RECONNECT_BASE_DELAY = 1000;
const RECONNECT_MAX_DELAY = 16000;
const PING_INTERVAL = 30000;

export function useWebSocket(onMessage: (msg: WsMessage) => void) {
    const [connected, setConnected] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectDelay = useRef(RECONNECT_BASE_DELAY);
    const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const pingTimer = useRef<ReturnType<typeof setInterval> | null>(null);
    const onMessageRef = useRef(onMessage);
    onMessageRef.current = onMessage;

    const clearTimers = useCallback(() => {
        if (reconnectTimer.current) {
            clearTimeout(reconnectTimer.current);
            reconnectTimer.current = null;
        }
        if (pingTimer.current) {
            clearInterval(pingTimer.current);
            pingTimer.current = null;
        }
    }, []);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(`${WS_BASE_URL}/ws`);
        wsRef.current = ws;

        ws.onopen = () => {
            setConnected(true);
            reconnectDelay.current = RECONNECT_BASE_DELAY;

            pingTimer.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send("ping");
                }
            }, PING_INTERVAL);
        };

        ws.onmessage = (event) => {
            try {
                const msg: WsMessage = JSON.parse(event.data);
                if (msg.type === "pong") return;
                onMessageRef.current(msg);
            } catch {
                // ignore malformed messages
            }
        };

        ws.onclose = () => {
            setConnected(false);
            clearTimers();
            reconnectTimer.current = setTimeout(() => {
                reconnectDelay.current = Math.min(
                    reconnectDelay.current * 2,
                    RECONNECT_MAX_DELAY,
                );
                connect();
            }, reconnectDelay.current);
        };

        ws.onerror = () => {
            ws.close();
        };
    }, [clearTimers]);

    useEffect(() => {
        connect();
        return () => {
            clearTimers();
            wsRef.current?.close();
            wsRef.current = null;
        };
    }, [connect, clearTimers]);

    return { connected };
}
