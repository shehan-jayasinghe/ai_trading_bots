package com.aitrading.realtime.repository;

import com.aitrading.realtime.dto.ClientFilterDto;
import org.springframework.stereotype.Repository;
import org.springframework.web.socket.WebSocketSession;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class WebSocketSessionRepository {

    private final Map<String, ClientFilterDto> filters = new ConcurrentHashMap<>();
    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    public void register(WebSocketSession session, ClientFilterDto filter) {
        sessions.put(session.getId(), session);
        filters.put(session.getId(), filter != null ? filter : new ClientFilterDto(null, null));
    }

    public void remove(String sessionId) {
        sessions.remove(sessionId);
        filters.remove(sessionId);
    }

    public Optional<WebSocketSession> findById(String sessionId) {
        return Optional.ofNullable(sessions.get(sessionId));
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

    public ClientFilterDto getFilter(String sessionId) {
        return filters.getOrDefault(sessionId, new ClientFilterDto(null, null));
    }

    public void updateFilter(String sessionId, ClientFilterDto filter) {
        if (sessions.containsKey(sessionId)) {
            filters.put(sessionId, filter != null ? filter : new ClientFilterDto(null, null));
        }
    }

    public int countOpen() {
        return (int) sessions.values().stream().filter(WebSocketSession::isOpen).count();
    }
}
