package com.aitrading.realtime.repository;

import org.springframework.stereotype.Repository;
import org.springframework.web.socket.WebSocketSession;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class FlowSessionRepository {

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();
    private final Map<String, String> symbolFilter = new ConcurrentHashMap<>();

    public void register(WebSocketSession session, String symbol) {
        sessions.put(session.getId(), session);
        symbolFilter.put(session.getId(), symbol == null || symbol.isBlank() ? "BTCUSDT" : symbol.toUpperCase());
    }

    public void updateSymbol(String sessionId, String symbol) {
        if (sessions.containsKey(sessionId) && symbol != null && !symbol.isBlank()) {
            symbolFilter.put(sessionId, symbol.toUpperCase());
        }
    }

    public void remove(String sessionId) {
        sessions.remove(sessionId);
        symbolFilter.remove(sessionId);
    }

    public Map<String, WebSocketSession> findAllOpen() {
        Map<String, WebSocketSession> open = new ConcurrentHashMap<>();
        sessions.forEach((id, session) -> {
            if (session.isOpen()) {
                open.put(id, session);
            }
        });
        return open;
    }

    public String getSymbol(String sessionId) {
        return symbolFilter.getOrDefault(sessionId, "BTCUSDT");
    }

    public int countOpen() {
        return (int) sessions.values().stream().filter(WebSocketSession::isOpen).count();
    }
}
