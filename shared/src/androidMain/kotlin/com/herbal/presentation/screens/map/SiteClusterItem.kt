package com.herbal.presentation.screens.map

import com.google.android.gms.maps.model.LatLng
import com.google.maps.android.clustering.ClusterItem
import com.herbal.data.models.HeritageSite

data class SiteClusterItem(
    val site: HeritageSite,
    private val latLng: LatLng = LatLng(site.latitude!!, site.longitude!!),
    private val title: String = site.name,
    private val snippet: String = site.location ?: ""
) : ClusterItem {
    override fun getPosition(): LatLng = latLng
    override fun getTitle(): String = title
    override fun getSnippet(): String = snippet
    override fun getZIndex(): Float? {
        return if (site.latitude != null && site.longitude != null) 1f else null
    }
}