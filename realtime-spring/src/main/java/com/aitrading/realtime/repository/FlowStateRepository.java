package com.aitrading.realtime.repository;

import com.aitrading.realtime.dto.FlowSnapshotDto;
import org.springframework.stereotype.Repository;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

@Repository
public class FlowStateRepository {

    private final Map<String, FlowSnapshotDto> bySymbol = new ConcurrentHashMap<>();

    public void upsert(FlowSnapshotDto snapshot) {
        if (snapshot.symbol() != null) {
            bySymbol.put(snapshot.symbol().toUpperCase(), snapshot);
        }
    }

    public Optional<FlowSnapshotDto> findBySymbol(String symbol) {
        return Optional.ofNullable(bySymbol.get(symbol.toUpperCase()));
    }

    public Map<String, FlowSnapshotDto> findAll() {
        return Map.copyOf(bySymbol);
    }
}
