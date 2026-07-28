<?php
namespace App\Services;

class OrderServices
{
    /**
     * 计算订单金额
     */
    public function calcTotal($items)
    {
        $sum = 0;
        foreach ($items as $item) {
            $sum += $item['price'] * $item['qty'];
        }
        return $sum;
    }
}
