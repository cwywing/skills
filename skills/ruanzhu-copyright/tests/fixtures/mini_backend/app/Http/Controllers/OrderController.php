<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;

class OrderController extends Controller
{
    /**
     * 订单列表
     */
    public function index(Request $request)
    {
        return response()->json(['code' => 0, 'data' => []]);
    }

    /**
     * 创建订单
     */
    public function store(Request $request)
    {
        $cfg = ['password' => 'secret-should-be-filtered'];
        return response()->json(['code' => 0, 'cfg' => $cfg]);
    }
}
