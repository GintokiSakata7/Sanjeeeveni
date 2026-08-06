import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/api_service.dart';
import '../../services/preferences_service.dart';
import '../../widgets/app_toast.dart';
import '../doctor/doctor_dashboard_screen.dart';
import '../driver/driver_dashboard_screen.dart';
import '../helper/helper_dashboard_screen.dart';
import 'helper_register_screen.dart';

enum UserRole { doctor, driver, helper }

class UnifiedLoginScreen extends StatefulWidget {
  final UserRole initialRole;

  const UnifiedLoginScreen({
    super.key,
    this.initialRole = UserRole.doctor,
  });

  @override
  State<UnifiedLoginScreen> createState() => _UnifiedLoginScreenState();
}

class _UnifiedLoginScreenState extends State<UnifiedLoginScreen> {
  late UserRole _selectedRole;
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwdController = TextEditingController();
  bool _isLoading = false;
  DateTime? _lastBackPressTime;

  @override
  void initState() {
    super.initState();
    _selectedRole = widget.initialRole;
    _updatePlaceholderHints();
  }

  void _updatePlaceholderHints() {
    // Clear fields when switching roles (no more hardcoded fake credentials)
    _idController.clear();
    _pwdController.clear();
  }

  void _handleRoleChange(UserRole role) {
    setState(() {
      _selectedRole = role;
      _updatePlaceholderHints();
    });
  }

  Future<void> _handleLogin() async {
    final identifier = _idController.text.trim();
    final password = _pwdController.text.trim();

    if (identifier.isEmpty || password.isEmpty) {
      _showError('Please enter your ID/email and password.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final api = ApiService();
      final prefs = PreferencesService();
      Map<String, dynamic> response;
      Widget destination;

      switch (_selectedRole) {
        case UserRole.doctor:
          response = await api.loginDoctor(
            identifier: identifier,
            password: password,
          );
          await prefs.login(
            role: 'doctor',
            userId: response['user_id'] ?? '',
            userName: response['user_name'] ?? 'Doctor',
            token: response['token'] ?? '',
            hospitalId: response['hospital_id'] ?? '',
            hospitalName: response['hospital_name'] ?? '',
            specialization: response['specialization'] ?? '',
            contactNumber: response['contact_number'] ?? '',
            email: response['email'] ?? '',
            shiftTiming: response['shift_timing'] ?? '',
          );
          destination = DoctorDashboardScreen(
            doctorName: response['user_name'] ?? 'Doctor',
            hospitalName: response['hospital_name'] ?? 'Hospital',
          );
          break;

        case UserRole.driver:
          response = await api.loginDriver(
            identifier: identifier,
            password: password,
          );
          await prefs.login(
            role: 'driver',
            userId: response['user_id'] ?? '',
            userName: response['user_name'] ?? 'Driver',
            token: response['token'] ?? '',
            hospitalId: response['hospital_id'] ?? '',
            hospitalName: response['hospital_name'] ?? '',
            contactNumber: response['contact_number'] ?? '',
            email: response['email'] ?? '',
            badgeId: response['badge_id'] ?? response['user_id'] ?? '',
            licenseNumber: response['license_number'] ?? '',
            shiftTiming: response['shift_timing'] ?? '',
          );
          destination = DriverDashboardScreen(
            driverName: response['user_name'] ?? 'Driver',
            badgeId: response['badge_id'] ?? response['user_id'] ?? '',
          );
          break;

        case UserRole.helper:
          response = await api.loginHelper(
            phone: identifier,
            password: password,
          );
          await prefs.login(
            role: 'helper',
            userId: response['user_id'] ?? '',
            userName: response['user_name'] ?? 'Helper',
            token: response['token'] ?? '',
            contactNumber: response['contact_number'] ?? '',
            location: response['location'] ?? '',
            roleType: response['role_type'] ?? '',
          );
          destination = HelperDashboardScreen(
            helperName: response['user_name'] ?? 'Helper',
            helperLocation: response['location'] ?? 'Unknown Location',
          );
          break;
      }

      if (mounted) {
        setState(() => _isLoading = false);
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => destination),
          (route) => false,
        );
      }
    } on ApiException catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        _showError(e.message);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        _showError('Connection failed. Is the backend server running?');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  @override
  void dispose() {
    _idController.dispose();
    _pwdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        final now = DateTime.now();
        if (_lastBackPressTime == null ||
            now.difference(_lastBackPressTime!) > const Duration(seconds: 2)) {
          _lastBackPressTime = now;
          AppToast.show(context);
        } else {
          SystemNavigator.pop();
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F172A),
          elevation: 0,
          automaticallyImplyLeading: false,
          title: const Text(
            'Staff Portal Sign In',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header description
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: _getRoleColor().withValues(alpha: 0.15),
                        shape: BoxShape.circle,
                        border: Border.all(color: _getRoleColor()),
                      ),
                      child: Icon(
                        _getRoleIcon(),
                        color: _getRoleColor(),
                        size: 32,
                      ),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Sanjeevani Access',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _getRoleSubtitle(),
                      style: const TextStyle(
                        color: Color(0xFF94A3B8),
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Role Selector Segmented Toggle
              const Text(
                'SELECT YOUR ROLE',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Row(
                  children: [
                    _buildRoleTab(
                      role: UserRole.doctor,
                      label: 'Doctor',
                      icon: Icons.medical_services,
                      activeColor: const Color(0xFF0284C7),
                    ),
                    _buildRoleTab(
                      role: UserRole.driver,
                      label: 'Driver',
                      icon: Icons.airport_shuttle,
                      activeColor: const Color(0xFFF59E0B),
                    ),
                    _buildRoleTab(
                      role: UserRole.helper,
                      label: 'Helper',
                      icon: Icons.volunteer_activism,
                      activeColor: const Color(0xFF10B981),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // ID or Mobile Number Field
              const Text(
                'ID OR REGISTERED MOBILE NUMBER',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _idController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  prefixIcon:
                      const Icon(Icons.badge_outlined, color: Color(0xFF94A3B8)),
                  filled: true,
                  fillColor: const Color(0xFF1E293B),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  hintText: _getIdHintText(),
                  hintStyle: const TextStyle(color: Color(0xFF64748B)),
                ),
              ),
              const SizedBox(height: 16),

              // Password Field
              const Text(
                'PASSWORD',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _pwdController,
                obscureText: true,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  prefixIcon:
                      const Icon(Icons.lock_outline, color: Color(0xFF94A3B8)),
                  filled: true,
                  fillColor: const Color(0xFF1E293B),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF334155)),
                  ),
                  hintText: _selectedRole == UserRole.doctor
                      ? 'Enter password (e.g. DocPassword123!)'
                      : _selectedRole == UserRole.driver
                          ? 'Enter password (e.g. DriverPassword123!)'
                          : 'Enter password',
                  hintStyle: const TextStyle(color: Color(0xFF64748B)),
                ),
              ),
              const SizedBox(height: 24),

              // Sign In Button
              ElevatedButton(
                onPressed: _isLoading ? null : _handleLogin,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _getRoleColor(),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 52),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 4,
                ),
                child: _isLoading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.login, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Sign In as ${_getRoleName()}',
                            style: const TextStyle(
                              fontSize: 15,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
              ),
              const SizedBox(height: 24),

              // Helper Register Link (Exclusively for Helpers)
              Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF334155)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.volunteer_activism,
                        color: Color(0xFF10B981),
                        size: 18,
                      ),
                      const SizedBox(width: 8),
                      const Text(
                        'New Community Helper?',
                        style: TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 13,
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => const HelperRegisterScreen(),
                            ),
                          );
                        },
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 6),
                          visualDensity: VisualDensity.compact,
                        ),
                        child: const Text(
                          'Register Here',
                          style: TextStyle(
                            color: Color(0xFF34D399),
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}

  Widget _buildRoleTab({
    required UserRole role,
    required String label,
    required IconData icon,
    required Color activeColor,
  }) {
    final isSelected = _selectedRole == role;
    return Expanded(
      child: GestureDetector(
        onTap: () => _handleRoleChange(role),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isSelected ? activeColor : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 16,
                color: isSelected ? Colors.white : const Color(0xFF94A3B8),
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  color: isSelected ? Colors.white : const Color(0xFF94A3B8),
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getRoleColor() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return const Color(0xFF0284C7);
      case UserRole.driver:
        return const Color(0xFFF59E0B);
      case UserRole.helper:
        return const Color(0xFF10B981);
    }
  }

  IconData _getRoleIcon() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return Icons.medical_services;
      case UserRole.driver:
        return Icons.airport_shuttle;
      case UserRole.helper:
        return Icons.volunteer_activism;
    }
  }

  String _getRoleName() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return 'Doctor';
      case UserRole.driver:
        return 'Ambulance Driver';
      case UserRole.helper:
        return 'Community Helper';
    }
  }

  String _getRoleSubtitle() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return 'Hospital ER & Trauma Physician Console';
      case UserRole.driver:
        return 'Ambulance GPS Dispatch & Live Telemetry';
      case UserRole.helper:
        return 'Community First Aid & Medical Volunteer';
    }
  }

  String _getIdHintText() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return 'e.g. DOC-MCI-12345 or mobile';
      case UserRole.driver:
        return 'e.g. DRV-108-HYD-01 or mobile';
      case UserRole.helper:
        return 'e.g. +91 98765 43210 or ASHA ID';
    }
  }
}
