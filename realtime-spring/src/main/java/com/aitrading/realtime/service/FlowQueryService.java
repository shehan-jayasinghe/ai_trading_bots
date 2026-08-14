package com.aitrading.realtime.service;

import com.aitrading.realtime.dto.FlowSnapshotDto;
import com.aitrading.realtime.exception.CandleProcessingException;
import com.aitrading.realtime.repository.FlowSessionRepository;
import com.aitrading.realtime.repository.FlowStateRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.WebSocketSession;

import java.util.Map;
import java.util.Optional;

@Service
public class FlowQueryService {

    private static final Logger log = LoggerFactory.getLogger(FlowQueryService.class);

    private final FlowStateRepository stateRepository;
    private final FlowBroadcastService broadcastService;
    private final FlowSessionRepository sessionRepository;
    private final ObjectMapper objectMapper;

    public FlowQueryService(
            FlowStateRepository stateRepository,
            FlowBroadcastService broadcastService,
            FlowSessionRepository sessionRepository,
            ObjectMapper objectMapper
    ) {
        this.stateRepository = stateRepository;
        this.broadcastService = broadcastService;
        this.sessionRepository = sessionRepository;
        this.objectMapper = objectMapper;
    }

    public void ingest(String rawJson) {
        try {
            FlowSnapshotDto dto = objectMapper.readValue(rawJson, FlowSnapshotDto.class);
            stateRepository.upsert(dto);
            broadcastService.broadcast(dto);
            log.debug("flow ingested symbol={} delta={} reaction={}", dto.symbol(), dto.delta(), dto.reaction());
        } catch (Exception ex) {
            throw new CandleProcessingException("Failed to deserialize flow JSON", ex);
        }
    }

    public Optional<FlowSnapshotDto> latest(String symbol) {
        return stateRepository.findBySymbol(symbol);
    }

    public Map<String, FlowSnapshotDto> all() {
        return stateRepository.findAll();
    }

    public void registerSession(WebSocketSession session, String symbol) {
        sessionRepository.register(session, symbol);
    }

    public void updateSymbol(String sessionId, String symbol) {
        sessionRepository.updateSymbol(sessionId, symbol);
    }

    public void removeSession(String sessionId) {
        sessionRepository.remove(sessionId);
    }

    public int openSessionCount() {
        return sessionRepository.countOpen();
    }
}
