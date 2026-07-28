<?php
namespace App\Models;

class Order extends MccModel
{
    protected $table = 'mcc_order';
    protected $primaryKey = 'id';
    protected $fillable = ['uid', 'order_sn', 'total_price', 'status'];
    protected $casts = ['total_price' => 'float', 'status' => 'int'];

    public function user()
    {
        return $this->belongsTo(User::class, 'uid', 'id');
    }

    /**
     * 按状态筛选订单
     */
    public function scopeStatus($query, $status)
    {
        return $query->where('status', $status);
    }
}
