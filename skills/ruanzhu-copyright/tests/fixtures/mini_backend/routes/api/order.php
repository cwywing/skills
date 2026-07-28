<?php

Route::get('order/list', [OrderController::class, 'index']);
Route::post('order/create', [OrderController::class, 'store']);
