import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator, Alert, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

const ListaDeudoresVencidos = () => {
  const navigation = useNavigation();

  const [deudores, setDeudores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDeudores = async () => {
    try {
      setLoading(true);
      setError(null);

      // Llama a la nueva API de deudores vencidos en tu backend FastAPI
      // Asegúrate que la IP y el puerto sean los correctos para tu API de Python (FastAPI)
      const response = await fetch('http://192.168.1.5:8000/deudores-vencidos'); 

      if (!response.ok) {
        const errorBody = await response.text();
        console.error(`ERROR HTTP: ${response.status} - ${response.statusText}. Cuerpo del error:`, errorBody);
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();

      if (data.exito) {
        setDeudores(data.datos);
      } else {
        console.error("La API reportó un error (data.exito es false):", data.mensaje);
        throw new Error(data.mensaje || 'Error al obtener los deudores.');
      }
    } catch (err) {
      console.error('Error CATCH en fetchDeudores:', err);
      setError('No se pudieron cargar los deudores. Intenta de nuevo más tarde.');
      Alert.alert('Error de Carga', 'No se pudieron cargar los deudores. Por favor, verifica tu conexión o inténtalo más tarde. Detalles: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeudores();
  }, []);

  const handleContactarWhatsApp = (telefono, nombreCliente, monto) => {
    // Formato del número para WhatsApp (sin el '+')
    // Asumiendo que el número ya viene con el código de país (ej. 5491123456789)
    const numeroWhatsApp = telefono.replace(/[^0-9]/g, ''); // Elimina cualquier caracter no numérico

    // Mensaje pre-llenado para WhatsApp
    const mensaje = `Hola ${nombreCliente}, te recordamos que tienes un pago de $${monto} pendiente con fecha de vencimiento pasada. Por favor, ponte al día para seguir disfrutando de nuestros servicios. ¡Gracias!`;
    const url = `whatsapp://send?phone=${numeroWhatsApp}&text=${encodeURIComponent(mensaje)}`;

    // Intenta abrir WhatsApp
    Linking.canOpenURL(url)
      .then(supported => {
        if (supported) {
          Linking.openURL(url);
        } else {
          Alert.alert('Error', 'WhatsApp no está instalado en tu dispositivo o no se pudo abrir.');
        }
      })
      .catch(err => console.error('Error al abrir WhatsApp:', err));
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#34C759" />
        <Text style={styles.loadingText}>Cargando deudores...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity onPress={fetchDeudores} style={styles.retryButton}>
          <Text style={styles.retryButtonText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="white" />
        </TouchableOpacity>
        <View style={styles.titleContainer}>
          <Text style={styles.title}>Deudores con Pagos Vencidos</Text>
        </View>
      </View>
      <ScrollView contentContainerStyle={styles.scrollViewContent}>
        {deudores.length === 0 ? (
          <Text style={styles.noDeudoresText}>¡No hay deudores con pagos vencidos!</Text>
        ) : (
          deudores.map((deudor, index) => ( // Usamos index como key si no hay un ID único en los datos deudores
            <View key={deudor.id || index} style={styles.deudorCard}>
              <Text style={styles.deudorNombre}>{deudor.nombre}</Text>
              <Text style={styles.deudorDetalle}>Plan: {deudor.plan}</Text>
              <Text style={styles.deudorDetalle}>Monto Adeudado: ${deudor.monto_adeudado.toFixed(2)}</Text>
              <Text style={styles.deudorDetalle}>Vencimiento: {deudor.fecha_vencimiento}</Text>
              <Text style={styles.deudorDetalle}>Teléfono: {deudor.telefono}</Text>
              <Text style={styles.deudorDetalle}>Estado: {deudor.estado_pago}</Text> {/* Muestra el estado */}
              <TouchableOpacity
                style={styles.whatsappButton}
                onPress={() => handleContactarWhatsApp(deudor.telefono, deudor.nombre, deudor.monto_adeudado)}
              >
                <Ionicons name="logo-whatsapp" size={20} color="white" style={styles.whatsappIcon} />
                <Text style={styles.whatsappButtonText}>Contactar por WhatsApp</Text>
              </TouchableOpacity>
            </View>
          ))
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#121214',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121214',
  },
  loadingText: {
    color: '#ffffff',
    marginTop: 10,
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121214',
    padding: 20,
  },
  errorText: {
    color: '#FF3B30',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#34C759',
    padding: 15,
    borderRadius: 10,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  backButton: {
    backgroundColor: 'transparent',
    padding: 10,
    marginRight: 10,
  },
  titleContainer: {
    flex: 1,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  scrollViewContent: {
    paddingBottom: 20,
  },
  deudorCard: {
    backgroundColor: '#1E1E1E',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#27272A',
  },
  deudorNombre: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#34C759',
    marginBottom: 5,
  },
  deudorDetalle: {
    fontSize: 16,
    color: '#E0E0E0',
    marginBottom: 3,
  },
  whatsappButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#25D366', // Color de WhatsApp
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
  },
  whatsappIcon: {
    marginRight: 8,
  },
  whatsappButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  noDeudoresText: {
    color: '#ffffff',
    fontSize: 18,
    textAlign: 'center',
    marginTop: 50,
  },
});

export default ListaDeudoresVencidos;
