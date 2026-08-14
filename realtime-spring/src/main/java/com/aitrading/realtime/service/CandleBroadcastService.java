package com.aitrading.realtime.service;

import com.aitrading.realtime.dto.CandleEnvelopeDto;
import com.aitrading.realtime.dto.ClientFilterDto;
import com.aitrading.realtime.repository.WebSocketSessionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.Map;

@Service
public class CandleBroadcastService {

    private static final Logger log = LoggerFactory.getLogger(CandleBroadcastService.class);

    private final WebSocketSessionRepository sessionRepository;
    private final ObjectMapper objectMapper;

    public CandleBroadcastService(WebSocketSessionRepository sessionRepository, ObjectMapper objectMapper) {
        this.sessionRepository = sessionRepository;
        this.objectMapper = objectMapper;
    }

    public void broadcast(CandleEnvelopeDto candle) {
        String json;
        try {
            json = objectMapper.writeValueAsString(candle);
        } catch (Exception ex) {
            log.error("Failed to serialize candle for websocket entity={} tf={}", candle.entity(), candle.timeframe(), ex);
            return;
        }

        TextMessage message = new TextMessage(json);
        int sent = 0;

        for (Map.Entry<String, WebSocketSession> entry : sessionRepository.findAllOpen().entrySet()) {
            String sessionId = entry.getKey();
            WebSocketSession session = entry.getValue();
            ClientFilterDto filter = sessionRepository.getFilter(sessionId);
            if (!filter.matches(candle)) {
                continue;
            }
            try {
                session.sendMessage(message);
                sent++;
            } catch (IOException ex) {
                log.warn("Failed to send websocket message sessionId={}", sessionId, ex);
            }
        }

        if (sent > 0) {
            log.trace("broadcast candle entity={} tf={} clients={}", candle.entity(), candle.timeframe(), sent);
        }
    }
}
