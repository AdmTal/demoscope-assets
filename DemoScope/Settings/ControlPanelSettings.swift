import Foundation
import Combine

// MARK: - ControlPanelSettings
//
// Centralized, observable settings model backed by UserDefaults.
//
// FIX: Previously, individual features (PiP, etc.) stored their toggle state
// but did not re-read it on the next session start. This class provides a
// single source of truth that publishes changes AND is always in sync with
// the persisted values when first accessed.
//
// Usage:
//   - Read:   ControlPanelSettings.shared.isPiPEnabled
//   - Write:  ControlPanelSettings.shared.isPiPEnabled = false
//   - Observe: ControlPanelSettings.shared.$isPiPEnabled.sink { ... }

final class ControlPanelSettings: ObservableObject {

    static let shared = ControlPanelSettings()

    private let defaults = UserDefaults.standard

    // ──────────────────────────────────────────────
    // MARK: Keys
    // ──────────────────────────────────────────────

    private enum Key: String {
        case isPiPEnabled           = "controlPanel_isPiPEnabled"
        case isMirrorEnabled        = "controlPanel_isMirrorEnabled"
        case isGridOverlayEnabled   = "controlPanel_isGridOverlayEnabled"
        case scrollSpeed            = "controlPanel_scrollSpeed"
        case fontSize               = "controlPanel_fontSize"
        case isAutoScrollEnabled    = "controlPanel_isAutoScrollEnabled"
        case isTeleprompterVisible  = "controlPanel_isTeleprompterVisible"
    }

    // ──────────────────────────────────────────────
    // MARK: Defaults (first-launch values)
    // ──────────────────────────────────────────────

    private static let defaultValues: [String: Any] = [
        Key.isPiPEnabled.rawValue:          true,
        Key.isMirrorEnabled.rawValue:       false,
        Key.isGridOverlayEnabled.rawValue:  false,
        Key.scrollSpeed.rawValue:           1.0,
        Key.fontSize.rawValue:              24.0,
        Key.isAutoScrollEnabled.rawValue:   true,
        Key.isTeleprompterVisible.rawValue: true,
    ]

    // ──────────────────────────────────────────────
    // MARK: Published properties
    //
    // Each property reads from / writes to UserDefaults so the persisted
    // value is ALWAYS authoritative. The @Published wrapper lets SwiftUI
    // views and Combine subscribers react to changes.
    // ──────────────────────────────────────────────

    @Published var isPiPEnabled: Bool {
        didSet { defaults.set(isPiPEnabled, forKey: Key.isPiPEnabled.rawValue) }
    }

    @Published var isMirrorEnabled: Bool {
        didSet { defaults.set(isMirrorEnabled, forKey: Key.isMirrorEnabled.rawValue) }
    }

    @Published var isGridOverlayEnabled: Bool {
        didSet { defaults.set(isGridOverlayEnabled, forKey: Key.isGridOverlayEnabled.rawValue) }
    }

    @Published var scrollSpeed: Double {
        didSet { defaults.set(scrollSpeed, forKey: Key.scrollSpeed.rawValue) }
    }

    @Published var fontSize: Double {
        didSet { defaults.set(fontSize, forKey: Key.fontSize.rawValue) }
    }

    @Published var isAutoScrollEnabled: Bool {
        didSet { defaults.set(isAutoScrollEnabled, forKey: Key.isAutoScrollEnabled.rawValue) }
    }

    @Published var isTeleprompterVisible: Bool {
        didSet { defaults.set(isTeleprompterVisible, forKey: Key.isTeleprompterVisible.rawValue) }
    }

    // ──────────────────────────────────────────────
    // MARK: Init — always reads persisted values
    // ──────────────────────────────────────────────

    private init() {
        // Register defaults so first-launch values are sensible.
        defaults.register(defaults: Self.defaultValues)

        // FIX: Read every value from UserDefaults on init so the in-memory
        // state matches what was persisted in the previous session.
        self.isPiPEnabled          = defaults.bool(forKey: Key.isPiPEnabled.rawValue)
        self.isMirrorEnabled       = defaults.bool(forKey: Key.isMirrorEnabled.rawValue)
        self.isGridOverlayEnabled  = defaults.bool(forKey: Key.isGridOverlayEnabled.rawValue)
        self.scrollSpeed           = defaults.double(forKey: Key.scrollSpeed.rawValue)
        self.fontSize              = defaults.double(forKey: Key.fontSize.rawValue)
        self.isAutoScrollEnabled   = defaults.bool(forKey: Key.isAutoScrollEnabled.rawValue)
        self.isTeleprompterVisible = defaults.bool(forKey: Key.isTeleprompterVisible.rawValue)
    }

    // ──────────────────────────────────────────────
    // MARK: Convenience — reset all to defaults
    // ──────────────────────────────────────────────

    func resetToDefaults() {
        for key in Self.defaultValues.keys {
            defaults.removeObject(forKey: key)
        }
        // Re-read so published properties update.
        isPiPEnabled          = defaults.bool(forKey: Key.isPiPEnabled.rawValue)
        isMirrorEnabled       = defaults.bool(forKey: Key.isMirrorEnabled.rawValue)
        isGridOverlayEnabled  = defaults.bool(forKey: Key.isGridOverlayEnabled.rawValue)
        scrollSpeed           = defaults.double(forKey: Key.scrollSpeed.rawValue)
        fontSize              = defaults.double(forKey: Key.fontSize.rawValue)
        isAutoScrollEnabled   = defaults.bool(forKey: Key.isAutoScrollEnabled.rawValue)
        isTeleprompterVisible = defaults.bool(forKey: Key.isTeleprompterVisible.rawValue)
    }
}
