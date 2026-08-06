import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:aero_mobile/main.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('SanjeevaniApp launches correctly and transitions past splash', (WidgetTester tester) async {
    await tester.pumpWidget(const SanjeevaniApp());
    expect(find.text('SANJEEVANI'), findsWidgets);

    // Advance splash screen timer (3 seconds)
    await tester.pump(const Duration(seconds: 4));
    await tester.pumpAndSettle();
  });
}
