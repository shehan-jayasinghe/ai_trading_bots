package com.aitrading.realtime.service;

import com.aitrading.realtime.dto.CandleEnvelopeDto;
import com.aitrading.realtime.dto.CandleOhlcvDto;
import com.aitrading.realtime.dto.ClientFilterDto;
import com.aitrading.realtime.entity.CandleEntity;
import com.aitrading.realtime.repository.CandleRepository;
import com.aitrading.realtime.repository.WebSocketSessionRepository;
import com.aitrading.realtime.validation.ClientFilterValidator;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.socket.WebSocketSession;

import java.util.Comparator;
import java.util.List;

@Service
public class CandleQueryService {

    private final CandleRepository candleRepository;
    private final WebSocketSessionRepository sessionRepository;
    private final ClientFilterValidator filterValidator;

    public CandleQueryService(
            CandleRepository candleRepository,
            WebSocketSessionRepository sessionRepository,
            ClientFilterValidator filterValidator
    ) {
        this.candleRepository = candleRepository;
        this.sessionRepository = sessionRepository;
        this.filterValidator = filterValidator;
    }

    @Transactional(readOnly = true)
    public List<CandleEnvelopeDto> recent(String entity, String timeframe) {
        return candleRepository.findTop200ByEntityAndTimeframeOrderByBucketEpochDesc(entity, timeframe)
                .stream()
                .sorted(Comparator.comparingLong(CandleEntity::getBucketEpoch))
                .map(this::toDto)
                .toList();
    }

    public void registerSession(WebSocketSession session, ClientFilterDto filter) {
        ClientFilterDto validated = filterValidator.validate(filter);
        sessionRepository.register(session, validated);
    }

    public void updateFilter(String sessionId, ClientFilterDto filter) {
        ClientFilterDto validated = filterValidator.validate(filter);
        sessionRepository.updateFilter(sessionId, validated);
    }

    public void removeSession(String sessionId) {
        sessionRepository.remove(sessionId);
    }

    public int openSessionCount() {
        return sessionRepository.countOpen();
    }

    private CandleEnvelopeDto toDto(CandleEntity entity) {
        return new CandleEnvelopeDto(
                entity.getEntity(),
                entity.getSource(),
                entity.getSymbol(),
                entity.getTimeframe(),
                entity.getBucketEpoch(),
                entity.getEventTimeMs(),
                new CandleOhlcvDto(
                        entity.getOpen(),
                        entity.getHigh(),
                        entity.getLow(),
                        entity.getClose(),
                        entity.getVolume(),
                        entity.getTradeCount()
                )
        );
    }
}
