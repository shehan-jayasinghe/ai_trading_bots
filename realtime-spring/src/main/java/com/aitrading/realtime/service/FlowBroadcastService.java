package com.aitrading.realtime.service;

import com.aitrading.realtime.dto.FlowSnapshotDto;
import com.aitrading.realtime.repository.FlowSessionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.Map;

@Service
public class FlowBroadcastService {

    private static final Logger log = LoggerFactory.getLogger(FlowBroadcastService.class);

    private final FlowSessionRepository sessionRepository;
    private final ObjectMapper objectMapper;

    public FlowBroadcastService(FlowSessionRepository sessionRepository, ObjectMapper objectMapper) {
        this.sessionRepository = sessionRepository;
        this.objectMapper = objectMapper;
    }

    public void broadcast(FlowSnapshotDto snapshot) {
        String json;
        try {
            json = objectMapper.writeValueAsString(snapshot);
        } catch (Exception ex) {
            log.error("Failed to serialize flow snapshot", ex);
            return;
        }
        TextMessage message = new TextMessage(json);
        String symbol = snapshot.symbol() == null ? "" : snapshot.symbol().toUpperCase();
        for (Map.Entry<String, WebSocketSession> entry : sessionRepository.findAllOpen().entrySet()) {
            String wanted = sessionRepository.getSymbol(entry.getKey());
            if (!wanted.equals(symbol)) {
                continue;
            }
            try {
                entry.getValue().sendMessage(message);
            } catch (IOException ex) {
                log.warn("Failed to send flow websocket sessionId={}", entry.getKey(), ex);
            }
        }
    }
}
