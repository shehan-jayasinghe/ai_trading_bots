package com.aitrading.realtime.service;

import com.aitrading.realtime.dto.CandleEnvelopeDto;
import com.aitrading.realtime.entity.CandleEntity;
import com.aitrading.realtime.repository.CandleRepository;
import com.aitrading.realtime.validation.CandleEnvelopeValidator;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CandleIngestService {

    private static final Logger log = LoggerFactory.getLogger(CandleIngestService.class);

    private final CandleRepository candleRepository;
    private final CandleBroadcastService broadcastService;
    private final CandleEnvelopeValidator candleValidator;
    private final ObjectMapper objectMapper;

    public CandleIngestService(
            CandleRepository candleRepository,
            CandleBroadcastService broadcastService,
            CandleEnvelopeValidator candleValidator,
            ObjectMapper objectMapper
    ) {
        this.candleRepository = candleRepository;
        this.broadcastService = broadcastService;
        this.candleValidator = candleValidator;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public void ingestFromKafka(String topic, String rawJson) {
        CandleEnvelopeDto dto = candleValidator.validate(parse(rawJson));
        persist(topic, dto);
        broadcastService.broadcast(dto);
        log.debug(
                "ingested candle entity={} tf={} bucket={} topic={}",
                dto.entity(),
                dto.timeframe(),
                dto.bucketEpoch(),
                topic
        );
    }

    private CandleEnvelopeDto parse(String rawJson) {
        try {
            return objectMapper.readValue(rawJson, CandleEnvelopeDto.class);
        } catch (Exception ex) {
            throw new com.aitrading.realtime.exception.CandleProcessingException(
                    "Failed to deserialize candle JSON",
                    ex
            );
        }
    }

    private void persist(String topic, CandleEnvelopeDto dto) {
        CandleEntity entity = candleRepository
                .findByEntityAndTimeframeAndBucketEpoch(dto.entity(), dto.timeframe(), dto.bucketEpoch())
                .orElseGet(CandleEntity::new);

        entity.setEntity(dto.entity());
        entity.setSource(dto.source());
        entity.setSymbol(dto.symbol());
        entity.setTimeframe(dto.timeframe());
        entity.setBucketEpoch(dto.bucketEpoch());
        entity.setEventTimeMs(dto.eventTimeMs());
        entity.setOpen(dto.payload().open());
        entity.setHigh(dto.payload().high());
        entity.setLow(dto.payload().low());
        entity.setClose(dto.payload().close());
        entity.setVolume(dto.payload().volume());
        entity.setTradeCount(dto.payload().tradeCount());
        entity.setKafkaTopic(topic);

        candleRepository.save(entity);
    }
}
