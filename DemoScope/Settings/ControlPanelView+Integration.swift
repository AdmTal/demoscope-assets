import SwiftUI

// MARK: - Control Panel Integration Guide
//
// This file shows how to wire the control panel toggles to
// ControlPanelSettings so that changes are persisted AND applied.
//
// FIX SUMMARY:
// The root cause of the PiP persistence bug (and similar issues) was that
// toggle state was stored in local @State variables that reset on each
// session, or was written to UserDefaults but never read back on init.
//
// The fix uses ControlPanelSettings.shared as the single source of truth:
//   1. Toggle binds directly to ControlPanelSettings @Published properties
//   2. Properties auto-persist to UserDefaults via didSet
//   3. On init, properties are loaded FROM UserDefaults
//   4. RecordingSessionManager.applyControlPanelSettings() reads them at
//      session start and configures each feature accordingly
//   5. PictureInPictureManager observes changes for real-time mid-session updates

// MARK: - Example SwiftUI Control Panel

/// Example control panel view. Replace your existing control panel toggles
/// with bindings to ControlPanelSettings.shared.
///
/// BEFORE (broken):
///   @State private var isPiPEnabled = true  // <-- resets every time!
///   Toggle("PiP", isOn: $isPiPEnabled)
///
/// AFTER (fixed):
///   @ObservedObject var settings = ControlPanelSettings.shared
///   Toggle("PiP", isOn: $settings.isPiPEnabled)  // <-- reads/writes UserDefaults
struct ControlPanelIntegrationExample: View {
    @ObservedObject private var settings = ControlPanelSettings.shared

    var body: some View {
        List {
            Section("Camera") {
                Toggle("Picture-in-Picture", isOn: $settings.isPiPEnabled)
                Toggle("Mirror Preview", isOn: $settings.isMirrorEnabled)
                Toggle("Grid Overlay", isOn: $settings.isGridOverlayEnabled)
            }

            Section("Teleprompter") {
                Toggle("Show Teleprompter", isOn: $settings.isTeleprompterVisible)
                Toggle("Auto-Scroll", isOn: $settings.isAutoScrollEnabled)

                HStack {
                    Text("Scroll Speed")
                    Slider(value: $settings.scrollSpeed, in: 0.25...4.0, step: 0.25)
                }

                HStack {
                    Text("Font Size")
                    Slider(value: $settings.fontSize, in: 14...48, step: 2)
                }
            }
        }
    }
}

// MARK: - Migration helper
//
// If your app previously stored settings under different UserDefaults keys,
// use this to migrate them on first launch after the update.

enum ControlPanelMigration {
    private static let migrationKey = "controlPanel_migrated_v1"

    static func migrateIfNeeded() {
        let defaults = UserDefaults.standard
        guard !defaults.bool(forKey: migrationKey) else { return }

        // Map old keys to new keys. Adjust these to match your prior key names.
        let keyMap: [(old: String, new: String)] = [
            ("pip_enabled",            "controlPanel_isPiPEnabled"),
            ("mirror_enabled",         "controlPanel_isMirrorEnabled"),
            ("grid_overlay_enabled",   "controlPanel_isGridOverlayEnabled"),
            ("scroll_speed",           "controlPanel_scrollSpeed"),
            ("font_size",              "controlPanel_fontSize"),
            ("auto_scroll_enabled",    "controlPanel_isAutoScrollEnabled"),
            ("teleprompter_visible",   "controlPanel_isTeleprompterVisible"),
        ]

        for (old, new) in keyMap {
            if defaults.object(forKey: old) != nil && defaults.object(forKey: new) == nil {
                defaults.set(defaults.object(forKey: old), forKey: new)
            }
        }

        defaults.set(true, forKey: migrationKey)
    }
}
