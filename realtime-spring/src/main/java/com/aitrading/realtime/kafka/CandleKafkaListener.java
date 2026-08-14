package com.aitrading.realtime.kafka;

import com.aitrading.realtime.exception.CandleProcessingException;
import com.aitrading.realtime.service.CandleIngestService;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class CandleKafkaListener {

    private static final Logger log = LoggerFactory.getLogger(CandleKafkaListener.class);

    private final CandleIngestService candleIngestService;

    public CandleKafkaListener(CandleIngestService candleIngestService) {
        this.candleIngestService = candleIngestService;
    }

    @KafkaListener(
            topics = {
                    "${app.kafka.topic-candles-btc}",
                    "${app.kafka.topic-candles-gold}"
            },
            groupId = "${spring.kafka.consumer.group-id}"
    )
    public void onCandle(ConsumerRecord<String, String> record) {
        try {
            candleIngestService.ingestFromKafka(record.topic(), record.value());
        } catch (CandleProcessingException ex) {
            log.warn("skip invalid kafka candle topic={} offset={} message={}",
                    record.topic(), record.offset(), ex.getMessage());
        } catch (Exception ex) {
            log.error("failed to process kafka candle topic={} offset={}",
                    record.topic(), record.offset(), ex);
        }
    }
}
