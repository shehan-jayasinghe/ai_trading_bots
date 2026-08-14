package com.aitrading.realtime.repository;

import com.aitrading.realtime.entity.CandleEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface CandleRepository extends JpaRepository<CandleEntity, Long> {

    Optional<CandleEntity> findByEntityAndTimeframeAndBucketEpoch(
            String entity,
            String timeframe,
            long bucketEpoch
    );

    List<CandleEntity> findTop200ByEntityAndTimeframeOrderByBucketEpochDesc(
            String entity,
            String timeframe
    );
}
