import 'package:flutter/material.dart';
import '../models/message.dart';
import '../widgets/user_message_bubble.dart';
import '../widgets/bot_message_bubble.dart';
import '../widgets/chat_input_field.dart';
import '../services/chat_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Message> _messages = [];
  final ChatService _chatService = ChatService.instance;
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _addWelcomeMessage() {
    final welcomeMessage = Message.bot(
      '''Xin chào! Tôi là **Dia5** - trợ lý AI chẩn đoán y tế.

Tôi có thể giúp bạn:
• Phân tích triệu chứng
• Đưa ra chẩn đoán sơ bộ  
• Tư vấn cách xử lý ban đầu
• Đánh giá mức độ cấp thiết

Hãy mô tả triệu chứng hoặc vấn đề sức khỏe bạn đang gặp phải.

*Lưu ý: Tôi chỉ hỗ trợ chẩn đoán sơ bộ, không thay thế ý kiến bác sĩ chuyên khoa.*''',
    );
    
    setState(() {
      _messages.insert(0, welcomeMessage);
    });
  }

  void _onSendMessage(String content) async {
    if (content.trim().isEmpty || _isLoading) return;

    // Add user message
    final userMessage = Message.user(content);
    setState(() {
      _messages.insert(0, userMessage);
      _isLoading = true;
    });

    // Add thinking indicator
    final thinkingMessage = Message.thinking();
    setState(() {
      _messages.insert(0, thinkingMessage);
    });

    _scrollToBottom();

    try {
      // Send user message to backend
      final userResult = await _chatService.sendUserMessage(content);
      if (userResult.isError) {
        throw Exception(userResult.error);
      }

      // Remove thinking message
      setState(() {
        _messages.removeAt(0);
      });

      // Stream AI response from chatbot
      String fullResponse = '';
      await for (final chunk in _chatService.streamChatResponse(content)) {
        fullResponse += chunk;
        
        setState(() {
          if (_messages.isEmpty || !_messages[0].isBot) {
            _messages.insert(0, Message.bot(fullResponse));
          } else {
            _messages[0] = Message.bot(fullResponse);
          }
        });
        
        _scrollToBottom();
      }

      // Save AI response to backend
      if (fullResponse.isNotEmpty) {
        await _chatService.saveAiResponse(fullResponse);
      }

      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      // Handle error
      setState(() {
        if (_messages.isNotEmpty && _messages[0].text.contains('🤔')) {
          _messages.removeAt(0); // Remove thinking message
        }
        _messages.insert(0, Message.bot(
          'Xin lỗi, đã có lỗi xảy ra khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.\n\nChi tiết lỗi: ${e.toString()}'
        ));
        _isLoading = false;
      });
    }

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          0.0,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        title: Row(
          children: [
            Container(
              width: 32.0,
              height: 32.0,
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
                border: Border.all(
                  color: Theme.of(context).primaryColor.withOpacity(0.3),
                  width: 1.0,
                ),
              ),
              child: Icon(
                Icons.medical_services_rounded,
                size: 18.0,
                color: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(width: 12.0),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dia5',
                  style: TextStyle(
                    fontSize: 18.0,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                Text(
                  'Trợ lý AI chẩn đoán',
                  style: TextStyle(
                    fontSize: 12.0,
                    color: Colors.grey,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {
              // TODO: Implement menu
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Chat Messages
          Expanded(
            child: _messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    reverse: true,
                    padding: const EdgeInsets.symmetric(vertical: 8.0),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      
                      if (message.sender == MessageSender.user) {
                        return UserMessageBubble(message: message);
                      } else {
                        return BotMessageBubble(message: message);
                      }
                    },
                  ),
          ),
          // Input Field
          ChatInputField(
            onSendMessage: _onSendMessage,
            isLoading: _isLoading,
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80.0,
              height: 80.0,
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                Icons.medical_services_rounded,
                size: 40.0,
                color: Theme.of(context).primaryColor,
              ),
            ),
            const SizedBox(height: 24.0),
            Text(
              'Xin chào! Tôi là Dia5',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 8.0),
            Text(
              'Hãy mô tả triệu chứng của bạn để tôi có thể hỗ trợ chẩn đoán sơ bộ',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey.shade600,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
