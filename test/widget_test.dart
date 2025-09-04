// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:ai_medical_diagnosis/main.dart';

void main() {
  testWidgets('Dia5 app smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const Dia5App());

    // Verify that our app has Bottom Navigation Bar
    expect(find.text('Chatbot'), findsOneWidget);
    expect(find.text('Tin tức'), findsOneWidget);
    expect(find.text('Hồ sơ'), findsOneWidget);

    // Verify that the chat screen is initially shown
    expect(find.text('Dia5'), findsOneWidget);
  });
}
