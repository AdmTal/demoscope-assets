import AVKit
import Combine
import UIKit

// MARK: - PictureInPictureManager
//
// Manages the PiP lifecycle and ensures it respects persisted settings.
//
// FIX: Previously, PiP was started unconditionally in startSession().
// Now it checks ControlPanelSettings.shared.isPiPEnabled before activating,
// and observes setting changes so toggling mid-session works immediately.

final class PictureInPictureManager {

    static let shared = PictureInPictureManager()

    private var pipController: AVPictureInPictureController?
    private var cancellables = Set<AnyCancellable>()
    private let settings = ControlPanelSettings.shared

    private init() {
        observeSettingChanges()
    }

    // ──────────────────────────────────────────────
    // MARK: Setup
    // ──────────────────────────────────────────────

    /// Call once when the camera preview layer is ready.
    func configure(with playerLayer: AVPlayerLayer) {
        guard AVPictureInPictureController.isPictureInPictureSupported() else { return }
        pipController = AVPictureInPictureController(playerLayer: playerLayer)
        pipController?.canStartPictureInPictureAutomaticallyFromInline = false
    }

    // ──────────────────────────────────────────────
    // MARK: Session lifecycle
    // ──────────────────────────────────────────────

    /// Called when a recording session starts.
    /// FIX: Only activates PiP if the persisted setting allows it.
    func onSessionStart() {
        guard settings.isPiPEnabled else {
            // Setting is off — make sure PiP is stopped.
            stopPiP()
            return
        }
        startPiP()
    }

    /// Called when a recording session ends.
    func onSessionEnd() {
        stopPiP()
    }

    // ──────────────────────────────────────────────
    // MARK: Start / Stop
    // ──────────────────────────────────────────────

    func startPiP() {
        guard let pip = pipController,
              pip.isPictureInPicturePossible,
              !pip.isPictureInPictureActive else { return }
        pip.startPictureInPicture()
    }

    func stopPiP() {
        guard let pip = pipController,
              pip.isPictureInPictureActive else { return }
        pip.stopPictureInPicture()
    }

    // ──────────────────────────────────────────────
    // MARK: Observe setting changes (mid-session toggle)
    // ──────────────────────────────────────────────

    /// FIX: Reacts to control-panel toggle changes in real time so the user
    /// sees immediate feedback whether they toggle during a session or before.
    private func observeSettingChanges() {
        settings.$isPiPEnabled
            .dropFirst() // skip the initial value (handled by onSessionStart)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] enabled in
                if enabled {
                    self?.startPiP()
                } else {
                    self?.stopPiP()
                }
            }
            .store(in: &cancellables)
    }
}
