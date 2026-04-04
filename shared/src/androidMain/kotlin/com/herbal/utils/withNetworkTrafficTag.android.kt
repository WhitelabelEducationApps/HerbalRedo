package com.herbal.utils

import android.net.TrafficStats

actual fun <T> withNetworkTrafficTag(block: () -> T): T {
    // A unique tag for your network requests. Can be any integer.
    val tag = 0x9000

    // setThreadStatsTag was added in API 14
    TrafficStats.setThreadStatsTag(tag)
    try {
        return block()
    } finally {
        // Always clear the tag to avoid accidentally tagging other network operations.
        TrafficStats.clearThreadStatsTag()
    }
}