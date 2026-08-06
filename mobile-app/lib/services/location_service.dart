import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';

class LocationService {
  /// Get the device's current GPS position.
  /// Returns null if permission is denied or location services are off.
  static Future<Position?> getCurrentPosition() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      return null;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return null;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      return null;
    }

    return await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
      ),
    );
  }

  /// Calculate distance in meters between two GPS points.
  static double distanceInMeters({
    required double fromLat,
    required double fromLng,
    required double toLat,
    required double toLng,
  }) {
    return Geolocator.distanceBetween(fromLat, fromLng, toLat, toLng);
  }

  /// Format distance for display (meters or km).
  static String formatDistance(double meters) {
    if (meters < 1000) {
      return '${meters.round()} m';
    } else {
      return '${(meters / 1000).toStringAsFixed(1)} km';
    }
  }

  /// Estimate walking time (avg 5 km/h).
  static String estimateWalkingTime(double meters) {
    final minutes = (meters / 1000 / 5 * 60).round();
    if (minutes < 1) return 'Less than 1 min';
    if (minutes == 1) return '1 min walk';
    return '$minutes min walk';
  }

  /// Estimate driving time (avg 30 km/h in city).
  static String estimateDrivingTime(double meters) {
    final minutes = (meters / 1000 / 30 * 60).round();
    if (minutes < 1) return 'Less than 1 min';
    if (minutes == 1) return '1 min drive';
    return '$minutes min drive';
  }

  /// Open Google Maps with directions from user's current position to destination.
  /// [travelMode] can be 'walking' or 'driving'.
  static Future<void> openGoogleMapsDirections({
    required double destinationLat,
    required double destinationLng,
    String travelMode = 'walking',
  }) async {
    final position = await getCurrentPosition();

    String originParam = '';
    if (position != null) {
      originParam = '&origin=${position.latitude},${position.longitude}';
    }

    final url = Uri.parse(
      'https://www.google.com/maps/dir/?api=1'
      '$originParam'
      '&destination=$destinationLat,$destinationLng'
      '&travelmode=$travelMode',
    );

    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }
}
