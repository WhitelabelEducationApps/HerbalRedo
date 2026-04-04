package com.herbal.utils

/**
 * Executes a block of code, applying a network traffic tag on supported platforms (Android).
 *
 * @param block The code to execute, which may perform network operations.
 */
expect fun <T> withNetworkTrafficTag(block: () -> T): T
