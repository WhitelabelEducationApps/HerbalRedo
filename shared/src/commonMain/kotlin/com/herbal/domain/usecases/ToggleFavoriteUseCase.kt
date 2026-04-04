package com.herbal.domain.usecases

import com.herbal.data.models.HeritageSite
import com.whitelabel.core.domain.usecase.ToggleFavoriteUseCase as CoreToggleFavoriteUseCase

typealias ToggleFavoriteUseCase = CoreToggleFavoriteUseCase<HeritageSite>
