package com.aitrading.realtime.controller;

import com.aitrading.realtime.dto.ClientFilterDto;
import com.aitrading.realtime.service.CandleQueryService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

@Component
public class CandleWebSocketHandler extends TextWebSocketHandler {

    private static final Logger log = LoggerFactory.getLogger(CandleWebSocketHandler.class);

    private final CandleQueryService candleQueryService;
    private final ObjectMapper objectMapper;

    public CandleWebSocketHandler(CandleQueryService candleQueryService, ObjectMapper objectMapper) {
        this.candleQueryService = candleQueryService;
        this.objectMapper = objectMapper;
    }

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        candleQueryService.registerSession(session, new ClientFilterDto(null, null));
        log.info("websocket connected sessionId={} remote={}", session.getId(), session.getRemoteAddress());
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        ClientFilterDto filter = objectMapper.readValue(message.getPayload(), ClientFilterDto.class);
        candleQueryService.updateFilter(session.getId(), filter);
        log.debug("websocket filter updated sessionId={} entity={} timeframe={}",
                session.getId(), filter.entity(), filter.timeframe());
        session.sendMessage(new TextMessage("{\"status\":\"filter_updated\"}"));
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        candleQueryService.removeSession(session.getId());
        log.info("websocket closed sessionId={} status={}", session.getId(), status);
    }

    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) {
        log.warn("websocket transport error sessionId={}", session.getId(), exception);
        candleQueryService.removeSession(session.getId());
    }
}
