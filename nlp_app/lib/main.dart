import 'package:flutter/material.dart';

void main() {
  runApp(const NLPApp());
}

class NLPApp extends StatelessWidget {
  const NLPApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NLP App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const NLPHomePage(title: 'Natural Language Processing App'),
    );
  }
}

class NLPHomePage extends StatefulWidget {
  const NLPHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<NLPHomePage> createState() => _NLPHomePageState();
}

class _NLPHomePageState extends State<NLPHomePage> {
  String _processedText = 'Enter text to process...';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Text(
                _processedText,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 20),
              TextField(
                decoration: const InputDecoration(
                  hintText: 'Enter text for NLP processing...',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (value) {
                  // Process the text using Rust NLP
                  setState(() {
                    _processedText = processTextWithRust(value);
                  });
                },
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  // Process the text using Rust NLP
                  setState(() {
                    _processedText = processTextWithRust('Sample text for processing');
                  });
                },
                child: const Text('Process with Rust NLP'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String processTextWithRust(String input) {
    // This will be connected to the Rust NLP backend
    return 'Processed: $input';
  }
}