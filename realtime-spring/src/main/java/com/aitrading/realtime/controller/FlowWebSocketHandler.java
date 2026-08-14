package com.aitrading.realtime.controller;

import com.aitrading.realtime.service.FlowQueryService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

@Component
public class FlowWebSocketHandler extends TextWebSocketHandler {

    private static final Logger log = LoggerFactory.getLogger(FlowWebSocketHandler.class);

    private final FlowQueryService flowQueryService;
    private final ObjectMapper objectMapper;

    public FlowWebSocketHandler(FlowQueryService flowQueryService, ObjectMapper objectMapper) {
        this.flowQueryService = flowQueryService;
        this.objectMapper = objectMapper;
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        flowQueryService.registerSession(session, "BTCUSDT");
        log.info("flow websocket connected sessionId={}", session.getId());
        flowQueryService.latest("BTCUSDT").ifPresent(snapshot -> {
            try {
                session.sendMessage(new TextMessage(objectMapper.writeValueAsString(snapshot)));
            } catch (Exception ex) {
                log.warn("failed to send initial flow snapshot", ex);
            }
        });
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        JsonNode node = objectMapper.readTree(message.getPayload());
        String symbol = node.path("symbol").asText("BTCUSDT");
        flowQueryService.updateSymbol(session.getId(), symbol);
        session.sendMessage(new TextMessage("{\"status\":\"filter_updated\"}"));
        flowQueryService.latest(symbol).ifPresent(snapshot -> {
            try {
                session.sendMessage(new TextMessage(objectMapper.writeValueAsString(snapshot)));
            } catch (Exception ex) {
                log.warn("failed to send flow snapshot after filter", ex);
            }
        });
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        flowQueryService.removeSession(session.getId());
        log.info("flow websocket closed sessionId={}", session.getId());
    }

    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) {
        log.warn("flow websocket error sessionId={}", session.getId(), exception);
        flowQueryService.removeSession(session.getId());
    }
}
