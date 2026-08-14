package com.aitrading.realtime.kafka;

import com.aitrading.realtime.exception.CandleProcessingException;
import com.aitrading.realtime.service.FlowQueryService;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class FlowKafkaListener {

    private static final Logger log = LoggerFactory.getLogger(FlowKafkaListener.class);

    private final FlowQueryService flowQueryService;

    public FlowKafkaListener(FlowQueryService flowQueryService) {
        this.flowQueryService = flowQueryService;
    }

    @KafkaListener(
            topics = "${app.kafka.topic-market-flow}",
            groupId = "${spring.kafka.consumer.group-id}-flow"
    )
    public void onFlow(ConsumerRecord<String, String> record) {
        try {
            flowQueryService.ingest(record.value());
        } catch (CandleProcessingException ex) {
            log.warn("skip invalid flow record offset={} message={}", record.offset(), ex.getMessage());
        } catch (Exception ex) {
            log.error("failed to process flow record offset={}", record.offset(), ex);
        }
    }
}
