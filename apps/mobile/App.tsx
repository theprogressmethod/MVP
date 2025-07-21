import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

export default function App() {
  const handleCreateCommitment = () => {
    // This will be connected to Supabase later
    console.log('Creating commitment...');
  };

  const handleViewPods = () => {
    console.log('Viewing pods...');
  };

  return (
    <View style={styles.container}>
      <StatusBar style="auto" />
      
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>The Progress Method</Text>
        <Text style={styles.subtitle}>Track your weekly commitments</Text>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        
        {/* Welcome Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>🚀 MVP Setup Complete!</Text>
          <Text style={styles.cardText}>
            This React Native app is part of The Progress Method monorepo with:
          </Text>
          <View style={styles.features}>
            <Text style={styles.feature}>✅ Offline-first architecture</Text>
            <Text style={styles.feature}>✅ TypeScript integration</Text>
            <Text style={styles.feature}>✅ Shared types with web admin</Text>
            <Text style={styles.feature}>✅ Supabase database ready</Text>
            <Text style={styles.feature}>⏳ Pod management system</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Quick Actions</Text>
          
          <TouchableOpacity style={styles.primaryButton} onPress={handleCreateCommitment}>
            <Text style={styles.buttonText}>📝 Create This Week's Commitment</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.secondaryButton} onPress={handleViewPods}>
            <Text style={styles.secondaryButtonText}>🫘 View My Pods</Text>
          </TouchableOpacity>
        </View>

        {/* Status Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Development Status</Text>
          <View style={styles.statusGrid}>
            <View style={styles.statusItem}>
              <Text style={styles.statusNumber}>0</Text>
              <Text style={styles.statusLabel}>Commitments</Text>
            </View>
            <View style={styles.statusItem}>
              <Text style={styles.statusNumber}>0</Text>
              <Text style={styles.statusLabel}>Active Pods</Text>
            </View>
            <View style={styles.statusItem}>
              <Text style={styles.statusNumber}>🔧</Text>
              <Text style={styles.statusLabel}>In Development</Text>
            </View>
          </View>
        </View>

        {/* Connection Status */}
        <View style={[styles.card, styles.warningCard]}>
          <Text style={styles.warningTitle}>🏗️ Under Construction</Text>
          <Text style={styles.warningText}>
            Backend integration and offline sync will be implemented in Phase 1 development.
            Currently showing UI structure and monorepo integration.
          </Text>
        </View>

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    backgroundColor: '#1e293b',
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 5,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 20,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 12,
  },
  cardText: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: 12,
    lineHeight: 24,
  },
  features: {
    marginTop: 8,
  },
  feature: {
    fontSize: 14,
    color: '#475569',
    marginBottom: 6,
    lineHeight: 20,
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginBottom: 12,
  },
  secondaryButton: {
    backgroundColor: '#f1f5f9',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  secondaryButtonText: {
    color: '#475569',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  statusGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 12,
  },
  statusItem: {
    alignItems: 'center',
  },
  statusNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  statusLabel: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 4,
  },
  warningCard: {
    backgroundColor: '#fefce8',
    borderColor: '#facc15',
    borderWidth: 1,
  },
  warningTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#a16207',
    marginBottom: 8,
  },
  warningText: {
    fontSize: 14,
    color: '#a16207',
    lineHeight: 20,
  },
});