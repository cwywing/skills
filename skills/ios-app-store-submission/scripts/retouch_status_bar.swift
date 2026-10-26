// App Store 截图状态栏修图:把充电中的电池换成干净的满电电池(去闪电)。
// 模拟器 `simctl status_bar override` 在 iOS 26+ 上命令成功但不生效,只能事后修图。
//
// 用法: swift retouch_status_bar.swift shot1.png shot2.png ...
// 原理: 在顶部 250 行内按"绿色像素"定位旧电池 → 就近采样背景色紧贴擦除 →
//       按原尺寸重画满电电池。自动适配 iPhone(1320 宽)与 iPad(2064 宽)。
//
// 已知坑(踩过):
//  - AppKit 的 NSBitmapImageRep y 轴向下,CoreGraphics y 轴向上——混用两种坐标系
//    会把图形画到图底部。本脚本统一:检测用 rep(向下),绘制换算 y_cg = h - y_top。
//  - NSImage lockFocus 二次绘制会产出错位图;只有 NSBitmapImageRep+NSGraphicsContext
//    或纯 CG(本脚本)可靠。
//  - 擦除框要贴着电池(±stroke 宽),采样点在框左侧 5px,否则在渐变背景上露色块。
//  - 上传前要去 alpha(asc screenshots upload 拒绝带透明通道的 PNG)。

import AppKit
import CoreGraphics

let paths = CommandLine.arguments.dropFirst()
for path in paths {
    guard let data = FileManager.default.contents(atPath: path),
          let src = CGImageSourceCreateWithData(data as CFData, nil),
          let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        fatalError("load \(path)")
    }
    let w = img.width, h = img.height
    let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                        bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
    let rep = NSBitmapImageRep(cgImage: ctx.makeImage()!)

    // 1) 顶部 250 行内找绿色电池 bbox(右 1/3 区域)
    var minX = Int.max, maxX = 0, minY = Int.max, maxY = 0
    for y in 0..<250 {
        for x in (w * 2 / 3)..<w {
            if let c = rep.colorAt(x: x, y: y) {
                let r = c.redComponent * 255, g = c.greenComponent * 255,
                    b = c.blueComponent * 255
                if g > 110 && g > r + 45 && g > b + 45 {
                    minX = min(minX, x); maxX = max(maxX, x)
                    minY = min(minY, y); maxY = max(maxY, y)
                }
            }
        }
    }
    guard minX < Int.max else { print("no battery: \(path)"); continue }
    let gw = CGFloat(maxX - minX), gh = CGFloat(maxY - minY)
    let cx = (CGFloat(minX) + CGFloat(maxX)) / 2
    let cy = (CGFloat(minY) + CGFloat(maxY)) / 2

    // 2) 紧贴擦除 + 就近采样
    let strokeW: CGFloat = max(4, gh * 0.18)
    let pad = strokeW / 2 + 3
    let ex0 = cx - gw / 2 - pad - strokeW, ex1 = cx + gw / 2 + pad + strokeW + gh * 0.45
    let ey0 = cy - gh / 2 - pad - strokeW, ey1 = cy + gh / 2 + pad + strokeW
    var bg = NSColor.white
    if let c = rep.colorAt(x: Int(ex0) - 5, y: Int(cy)) { bg = c }
    let fill = CGColor(red: bg.redComponent, green: bg.greenComponent,
                       blue: bg.blueComponent, alpha: 1)
    ctx.setFillColor(fill)
    ctx.fill(CGRect(x: ex0, y: CGFloat(h) - ey1, width: ex1 - ex0, height: ey1 - ey0))

    // 3) 按原尺寸画满电电池(CG y 向上:顶行 y_top 对应 y_cg = h - y1)
    let black = CGColor(srgbRed: 0, green: 0, blue: 0, alpha: 1)
    let green = CGColor(srgbRed: 52 / 255.0, green: 199 / 255.0, blue: 89 / 255.0, alpha: 1)
    let fx = CGFloat(minX), fy = CGFloat(h) - CGFloat(maxY)
    let inflate = strokeW / 2 + 1
    let outer = CGRect(x: fx - inflate, y: fy - inflate,
                       width: gw + inflate * 2, height: gh + inflate * 2)
    ctx.setStrokeColor(black)
    ctx.setLineWidth(strokeW)
    ctx.addPath(CGPath(roundedRect: outer, cornerWidth: gh * 0.28,
                       cornerHeight: gh * 0.28, transform: nil))
    ctx.strokePath()
    let nubW = max(5, gh * 0.22), nubH = gh * 0.5
    ctx.setFillColor(black)
    ctx.addPath(CGPath(roundedRect: CGRect(x: outer.maxX + 3, y: fy + gh / 2 - nubH / 2,
                                           width: nubW, height: nubH),
                       cornerWidth: 2, cornerHeight: 2, transform: nil))
    ctx.fillPath()
    ctx.setFillColor(green)
    ctx.addPath(CGPath(roundedRect: CGRect(x: fx, y: fy, width: gw, height: gh),
                       cornerWidth: gh * 0.2, cornerHeight: gh * 0.2, transform: nil))
    ctx.fillPath()

    let out = ctx.makeImage()!
    let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL,
                                               "public.png" as CFString, 1, nil)!
    CGImageDestinationAddImage(dest, out, nil)
    CGImageDestinationFinalize(dest)
    print("fixed \(path) battery@(\(minX)-\(maxX),\(minY)-\(maxY))")
}
