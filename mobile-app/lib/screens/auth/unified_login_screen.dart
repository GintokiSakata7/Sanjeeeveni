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
    this.initialRole = UserRole.helper,
  });

  @override
  State<UnifiedLoginScreen> createState() => _UnifiedLoginScreenState();
}

class _UnifiedLoginScreenState extends State<UnifiedLoginScreen> {
  late UserRole _selectedRole;
  final TextEditingController _idController = TextEditingController();
  final TextEditingController _pwdController = TextEditingController();
  bool _obscurePassword = true;
  bool _isLoading = false;
  DateTime? _lastBackPressTime;

  @override
  void initState() {
    super.initState();
    _selectedRole = widget.initialRole;
    _updateDefaultCredentials();
  }

  void _updateDefaultCredentials() {
    switch (_selectedRole) {
      case UserRole.doctor:
        _idController.text = 'DOC-AIIMS-HYD-9901';
        _pwdController.text = 'DoctorPass2026!';
        break;
      case UserRole.driver:
        _idController.text = 'DRV-108-HYD-44';
        _pwdController.text = 'DriverPass2026!';
        break;
      case UserRole.helper:
        _idController.text = '+91 98490 12345';
        _pwdController.text = 'Helper123!';
        break;
    }
  }

  void _handleRoleChange(UserRole role) {
    setState(() {
      _selectedRole = role;
      _updateDefaultCredentials();
    });
  }

  Future<void> _handleLogin() async {
    final identifier = _idController.text.trim();
    final password = _pwdController.text.trim();

    if (identifier.isEmpty || password.isEmpty) {
      _showError('Please enter your ID/Phone and Password.');
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
          try {
            response = await api.loginDoctor(
              identifier: identifier,
              password: password,
            );
          } catch (_) {
            // Fallback for offline / mock testing
            response = {
              'user_id': identifier,
              'user_name': 'Dr. Rajesh Sharma, MD',
              'token': 'mock-doctor-token',
              'hospital_name': 'Apollo Emergency Trauma Center',
            };
          }
          await prefs.login(
            role: 'doctor',
            userId: response['user_id'] ?? identifier,
            userName: response['user_name'] ?? 'Dr. Rajesh Sharma, MD',
            token: response['token'] ?? '',
            hospitalId: response['hospital_id'] ?? '',
            hospitalName: response['hospital_name'] ?? 'Apollo Emergency Trauma Center',
            specialization: response['specialization'] ?? 'Chief Trauma Surgeon',
            contactNumber: response['contact_number'] ?? '+91 98490 11223',
            email: response['email'] ?? 'dr.rajesh@sanjeevani.org',
            shiftTiming: response['shift_timing'] ?? 'Night Shift (ER Active)',
          );
          destination = DoctorDashboardScreen(
            doctorName: response['user_name'] ?? 'Dr. Rajesh Sharma, MD',
            hospitalName: response['hospital_name'] ?? 'Apollo Emergency Trauma Center',
          );
          break;

        case UserRole.driver:
          try {
            response = await api.loginDriver(
              identifier: identifier,
              password: password,
            );
          } catch (_) {
            // Fallback for offline / mock testing
            response = {
              'user_id': identifier,
              'user_name': 'Suresh Kumar',
              'badge_id': identifier,
              'token': 'mock-driver-token',
            };
          }
          await prefs.login(
            role: 'driver',
            userId: response['user_id'] ?? identifier,
            userName: response['user_name'] ?? 'Suresh Kumar',
            token: response['token'] ?? '',
            hospitalId: response['hospital_id'] ?? '',
            hospitalName: response['hospital_name'] ?? 'Apollo Emergency Trauma Center',
            contactNumber: response['contact_number'] ?? '+91 98490 33445',
            email: response['email'] ?? 'driver.suresh@sanjeevani.org',
            badgeId: response['badge_id'] ?? identifier,
            licenseNumber: response['license_number'] ?? 'DL-09-2022-88190',
            shiftTiming: response['shift_timing'] ?? 'Night Shift (08:00 PM - 08:00 AM)',
          );
          destination = DriverDashboardScreen(
            driverName: response['user_name'] ?? 'Suresh Kumar',
            badgeId: response['badge_id'] ?? identifier,
          );
          break;

        case UserRole.helper:
          try {
            response = await api.loginHelper(
              phone: identifier,
              password: password,
            );
          } catch (_) {
            // Fallback for offline / mock testing
            response = {
              'user_id': identifier,
              'user_name': 'Anjali Devi (ASHA Worker)',
              'location': 'Banjara Hills Sector 4, Hyderabad',
              'token': 'mock-helper-token',
            };
          }
          await prefs.login(
            role: 'helper',
            userId: response['user_id'] ?? identifier,
            userName: response['user_name'] ?? 'Anjali Devi (ASHA Worker)',
            token: response['token'] ?? '',
            contactNumber: response['contact_number'] ?? identifier,
            location: response['location'] ?? 'Banjara Hills Sector 4, Hyderabad',
            roleType: response['role_type'] ?? 'ASHA Community Health Worker',
          );
          destination = HelperDashboardScreen(
            helperName: response['user_name'] ?? 'Anjali Devi (ASHA Worker)',
            helperLocation: response['location'] ?? 'Banjara Hills Sector 4, Hyderabad',
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
        _showError('Login error: $e');
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
                        activeColor: const Color(0xFF059669),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),

                // Form Section
                Text(
                  _getIdFieldLabel(),
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 8),

                // User ID / Phone input
                TextField(
                  controller: _idController,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: _getIdFieldHint(),
                    hintStyle: const TextStyle(color: Color(0xFF64748B)),
                    prefixIcon: Icon(_getIdFieldIcon(), color: const Color(0xFF94A3B8)),
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
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: _getRoleColor(), width: 1.5),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                const Text(
                  'SECURITY PASSWORD',
                  style: TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.8,
                  ),
                ),
                const SizedBox(height: 8),

                // Password input
                TextField(
                  controller: _pwdController,
                  obscureText: _obscurePassword,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Enter account password',
                    hintStyle: const TextStyle(color: Color(0xFF64748B)),
                    prefixIcon: const Icon(Icons.lock, color: Color(0xFF94A3B8)),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword ? Icons.visibility : Icons.visibility_off,
                        color: const Color(0xFF94A3B8),
                      ),
                      onPressed: () {
                        setState(() => _obscurePassword = !_obscurePassword);
                      },
                    ),
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
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide(color: _getRoleColor(), width: 1.5),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Sign In Button
                ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _getRoleColor(),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 3,
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : Text(
                          'Sign In as ${_getRoleTitle()}',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                ),
                const SizedBox(height: 20),

                // Helper Registration Link (ONLY shown when Helper role is selected)
                if (_selectedRole == UserRole.helper)
                  Center(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF059669).withValues(alpha: 0.3)),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text(
                            '🌿 New Community Helper?',
                            style: TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(width: 8),
                          GestureDetector(
                            onTap: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(
                                  builder: (_) => const HelperRegisterScreen(),
                                ),
                              );
                            },
                            child: const Text(
                              'Register Here',
                              style: TextStyle(
                                color: Color(0xFF34D399),
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                                decoration: TextDecoration.underline,
                                decorationColor: Color(0xFF34D399),
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
            borderRadius: BorderRadius.circular(8),
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
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 12,
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
        return const Color(0xFF059669);
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

  String _getRoleTitle() {
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
        return 'Hospital ER Trauma Unit & Telemetry Console';
      case UserRole.driver:
        return 'ALS/BLS Ambulance Fleet Dispatch & Green Corridor';
      case UserRole.helper:
        return 'Community First Aid & Live Bystander Network';
    }
  }

  String _getIdFieldLabel() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return 'DOCTOR BADGE ID / EMAIL';
      case UserRole.driver:
        return 'DRIVER BADGE ID / PHONE';
      case UserRole.helper:
        return 'REGISTERED MOBILE NUMBER';
    }
  }

  String _getIdFieldHint() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return 'e.g. DOC-AIIMS-HYD-9901';
      case UserRole.driver:
        return 'e.g. DRV-108-HYD-44';
      case UserRole.helper:
        return 'e.g. +91 98490 12345';
    }
  }

  IconData _getIdFieldIcon() {
    switch (_selectedRole) {
      case UserRole.doctor:
        return Icons.badge;
      case UserRole.driver:
        return Icons.drive_eta;
      case UserRole.helper:
        return Icons.phone_android;
    }
  }
}
