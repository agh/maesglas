import CoreText
import Foundation

let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let provider = CGDataProvider(url: url as CFURL),
      let graphicsFont = CGFont(provider) else {
    fatalError("Could not load the reference font")
}
let font = CTFontCreateWithGraphicsFont(graphicsFont, 15, nil, nil)
var character = UniChar(120)
var glyph = CGGlyph()
guard CTFontGetGlyphsForCharacters(font, &character, &glyph, 1) else {
    fatalError("The reference font has no x glyph")
}
var advance = CGSize()
CTFontGetAdvancesForGlyphs(font, .horizontal, &glyph, &advance, 1)
let result: [String: Double] = [
    "pointSize": Double(CTFontGetSize(font)),
    "cellWidth": Double(advance.width),
    "xHeight": Double(CTFontGetXHeight(font)),
]
guard abs(result["cellWidth"]! - 9) < 0.000001,
      abs(result["xHeight"]! - 8.1) < 0.000001 else {
    fatalError("CoreText metrics differ from the macOS reference")
}
let data = try JSONSerialization.data(withJSONObject: result, options: .sortedKeys)
print(String(decoding: data, as: UTF8.self))
