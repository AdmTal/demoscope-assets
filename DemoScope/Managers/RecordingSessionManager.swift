import Foundation
import Combine

// MARK: - RecordingSessionManager
//
// Coordinates session start/stop and ensures ALL control panel settings
// are applied from their persisted state when a new session begins.
//
// FIX: Previously, session startup did not re-read persisted settings,
// causing stale defaults (e.g. PiP always on) even when the user had
// toggled them off in a prior session.
//
// This file also serves as the integration guide — wire up each setting
// in applyControlPanelSettings() so no feature is missed.

final class RecordingSessionManager: ObservableObject {

    static let shared = RecordingSessionManager()

    @Published private(set) var isRecording = false

    private let settings = ControlPanelSettings.shared
    private let pipManager = PictureInPictureManager.shared
    private var cancellables = Set<AnyCancellable>()

    private init() {}

    // ──────────────────────────────────────────────
    // MARK: Session lifecycle
    // ──────────────────────────────────────────────

    func startSession() {
        // FIX: Apply all persisted settings BEFORE activating features.
        applyControlPanelSettings()
        isRecording = true
    }

    func stopSession() {
        isRecording = false
        pipManager.onSessionEnd()
    }

    // ──────────────────────────────────────────────
    // MARK: Apply persisted settings
    //
    // FIX: This is the core fix. Every control panel setting that affects
    // session behavior must be read and applied here. Add new settings
    // to this method as they are added to ControlPanelSettings.
    // ──────────────────────────────────────────────

    private func applyControlPanelSettings() {

        // --- PiP ---
        // FIX: This was the reported bug. PiP was always started on session
        // begin regardless of the saved toggle state. Now we delegate to the
        // PiP manager which checks the persisted setting.
        pipManager.onSessionStart()

        // --- Camera mirror ---
        // Apply the persisted mirror preference to the preview layer.
        applyCameraMirror(settings.isMirrorEnabled)

        // --- Grid overlay ---
        // Show or hide the composition grid based on persisted setting.
        applyGridOverlay(settings.isGridOverlayEnabled)

        // --- Teleprompter visibility ---
        // Show or hide the teleprompter overlay.
        applyTeleprompterVisibility(settings.isTeleprompterVisible)

        // --- Scroll speed ---
        // Apply the persisted teleprompter scroll speed.
        applyScrollSpeed(settings.scrollSpeed)

        // --- Font size ---
        // Apply the persisted teleprompter font size.
        applyFontSize(settings.fontSize)

        // --- Auto-scroll ---
        // Enable or disable auto-scroll on session start.
        applyAutoScroll(settings.isAutoScrollEnabled)
    }

    // ──────────────────────────────────────────────
    // MARK: Individual setting application
    //
    // Replace these stubs with your actual implementation calls.
    // Each method should talk to the relevant manager/view.
    // ──────────────────────────────────────────────

    private func applyCameraMirror(_ enabled: Bool) {
        // e.g. CameraManager.shared.setMirrored(enabled)
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "mirror", "value": enabled]
        )
    }

    private func applyGridOverlay(_ enabled: Bool) {
        // e.g. GridOverlayView.shared.isHidden = !enabled
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "gridOverlay", "value": enabled]
        )
    }

    private func applyTeleprompterVisibility(_ visible: Bool) {
        // e.g. TeleprompterView.shared.isHidden = !visible
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "teleprompterVisible", "value": visible]
        )
    }

    private func applyScrollSpeed(_ speed: Double) {
        // e.g. TeleprompterView.shared.scrollSpeed = speed
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "scrollSpeed", "value": speed]
        )
    }

    private func applyFontSize(_ size: Double) {
        // e.g. TeleprompterView.shared.fontSize = size
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "fontSize", "value": size]
        )
    }

    private func applyAutoScroll(_ enabled: Bool) {
        // e.g. TeleprompterView.shared.isAutoScrollEnabled = enabled
        NotificationCenter.default.post(
            name: .controlPanelSettingChanged,
            object: nil,
            userInfo: ["setting": "autoScroll", "value": enabled]
        )
    }
}

// MARK: - Notification for setting changes

extension Notification.Name {
    /// Posted when a control panel setting is applied at session start.
    /// Views/managers can observe this to update themselves.
    static let controlPanelSettingChanged = Notification.Name("controlPanelSettingChanged")
}
