import 'package:flutter/material.dart';

class LiveTrackerCard extends StatelessWidget {
  final String originLabel;
  final String destinationLabel;
  final String responderType; // 'Ambulance' or 'Community Helper'
  final double distanceKm;
  final int etaMinutes;
  final String corridorStatus;
  final VoidCallback? onExpandMap;

  const LiveTrackerCard({
    super.key,
    required this.originLabel,
    required this.destinationLabel,
    this.responderType = 'Ambulance',
    required this.distanceKm,
    required this.etaMinutes,
    this.corridorStatus = 'Green Corridor Active',
    this.onExpandMap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Simulated Map Canvas Header
          Container(
            height: 120,
            width: double.infinity,
            decoration: const BoxDecoration(
              color: Color(0xFF1E293B),
              borderRadius: BorderRadius.vertical(top: Radius.circular(15)),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF1E293B),
                  Color(0xFF0F172A),
                ],
              ),
            ),
            child: Stack(
              children: [
                // Simulated Grid Lines
                CustomPaint(
                  size: const Size(double.infinity, 120),
                  painter: _MapGridPainter(),
                ),

                // Corridor Status Pill
                Positioned(
                  top: 10,
                  left: 12,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF059669).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF10B981)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF10B981),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 6),
                        Text(
                          corridorStatus,
                          style: const TextStyle(
                            color: Color(0xFF10B981),
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Responder Icon Marker
                Positioned(
                  top: 45,
                  left: 60,
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFDC2626),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFFDC2626).withValues(alpha: 0.5),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: Icon(
                          responderType == 'Ambulance'
                              ? Icons.airport_shuttle
                              : Icons.directions_walk,
                          color: Colors.white,
                          size: 18,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        responderType,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                // Destination Patient Pin
                Positioned(
                  top: 35,
                  right: 50,
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0284C7),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF0284C7).withValues(alpha: 0.5),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.location_on,
                          color: Colors.white,
                          size: 20,
                        ),
                      ),
                      const SizedBox(height: 2),
                      const Text(
                        'Patient Scene',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

                // Expand Full Map Action
                if (onExpandMap != null)
                  Positioned(
                    bottom: 8,
                    right: 8,
                    child: InkWell(
                      onTap: onExpandMap,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.6),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Row(
                          children: [
                            Icon(Icons.fullscreen, color: Colors.white, size: 14),
                            SizedBox(width: 4),
                            Text(
                              'Live GPS View',
                              style: TextStyle(color: Colors.white, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),

          // Route Details Bar
          Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              children: [
                Row(
                  children: [
                    const Icon(Icons.radio_button_checked, color: Color(0xFF38BDF8), size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        originLabel,
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 12,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                Container(
                  margin: const EdgeInsets.only(left: 7),
                  height: 12,
                  width: 2,
                  color: const Color(0xFF475569),
                ),
                Row(
                  children: [
                    const Icon(Icons.location_pin, color: Color(0xFFEF4444), size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        destinationLabel,
                        style: const TextStyle(
                          color: Color(0xFFE2E8F0),
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                  ],
                ),
                const Divider(color: Color(0xFF334155), height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _MetricItem(
                      label: 'Remaining',
                      value: '$distanceKm km',
                      icon: Icons.route,
                    ),
                    Container(height: 24, width: 1, color: const Color(0xFF334155)),
                    _MetricItem(
                      label: 'Estimated ETA',
                      value: '$etaMinutes mins',
                      icon: Icons.timer,
                      highlight: true,
                    ),
                    Container(height: 24, width: 1, color: const Color(0xFF334155)),
                    const _MetricItem(
                      label: 'Live Speed',
                      value: '54 km/h',
                      icon: Icons.speed,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final bool highlight;

  const _MetricItem({
    required this.label,
    required this.value,
    required this.icon,
    this.highlight = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: highlight ? const Color(0xFF38BDF8) : const Color(0xFF94A3B8), size: 14),
            const SizedBox(width: 4),
            Text(
              value,
              style: TextStyle(
                color: highlight ? const Color(0xFF38BDF8) : Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ],
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF64748B),
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}

class _MapGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF334155).withValues(alpha: 0.4)
      ..strokeWidth = 1.0;

    for (double i = 0; i < size.width; i += 30) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double i = 0; i < size.height; i += 30) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);
    }

    // Simulated Route Line
    final routePaint = Paint()
      ..color = const Color(0xFF0284C7)
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round;

    canvas.drawLine(const Offset(68, 55), const Offset(150, 40), routePaint);
    canvas.drawLine(const Offset(150, 40), const Offset(260, 45), routePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
