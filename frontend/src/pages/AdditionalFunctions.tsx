import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  checkDeviceOnline,
  restartDevice,
  poweroffDevice,
  syncTime,
  testVoice,
  getMemoryInfo,
  clearAllData,
  getRecentAttendance,
  getDeviceTemplates,
} from '../api';
import {
  CommandCard,
  MemoryCard,
  RecentLogsCard,
  TemplatesCard,
} from '../components/device/FunctionCards';
import { useToast } from '../hooks/useToast';
import './AdditionalFunctions.css';

export function AdditionalFunctions() {
  const navigate = useNavigate();
  const toast = useToast();
  const [deviceId, setDeviceId] = useState<number | null>(null);
  const [deviceName, setDeviceName] = useState<string>('');
  const [isOnline, setIsOnline] = useState<boolean | null>(null);
  const [checkingOnline, setCheckingOnline] = useState(false);
  const [memoryInfo, setMemoryInfo] = useState<any>(null);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any>(null);
  const [loadingMemory, setLoadingMemory] = useState(false);
  const [loadingRecentLogs, setLoadingRecentLogs] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [processingCommand, setProcessingCommand] = useState(false);
  const [showNoSelection, setShowNoSelection] = useState(false);

  // Try to get device ID from localStorage on mount
  useEffect(() => {
    const lastDeviceId = localStorage.getItem('lastSelectedDeviceId');
    if (lastDeviceId) {
      setDeviceId(parseInt(lastDeviceId));
    } else {
      setShowNoSelection(true);
    }
  }, []);

  // Only check connection when deviceId is set AND user explicitly enters this page
  useEffect(() => {
    if (deviceId && isOnline === null) {
      checkDeviceStatus(deviceId);
    }
  }, [deviceId]);

  const checkDeviceStatus = async (id: number) => {
    setCheckingOnline(true);
    try {
      const result = await checkDeviceOnline(id);
      setIsOnline(result.online);
      setDeviceName(result.name);
      if (!result.online) {
        toast.warning(`⚠️ Dispositivo "${result.name}" está OFFLINE`);
      }
    } catch (error) {
      setIsOnline(false);
      toast.error('Error al verificar estado del dispositivo');
    } finally {
      setCheckingOnline(false);
    }
  };

  // Show message if no device selected
  if (showNoSelection) {
    return (
      <div className="additional-functions">
        <div className="no-selection">
          <h2>Selecciona una Terminal</h2>
          <p>Primero debes seleccionar una terminal de la lista de dispositivos para acceder a sus funciones adicionales.</p>
          <button 
            className="btn btn-primary"
            onClick={() => navigate('/devices')}
          >
            📱 Ir a la Lista de Terminales
          </button>
        </div>
      </div>
    );
  }

  if (!deviceId) {
    return <div className="additional-functions">Cargando...</div>;
  }

  // Still checking connection status
  if (checkingOnline || isOnline === null) {
    return (
      <div className="additional-functions">
        <div className="checking-status">
          <div className="spinner"></div>
          <p>Verificando estado de "{deviceName || 'Dispositivo'}"...</p>
        </div>
      </div>
    );
  }

  // If device is OFFLINE, show warning and options
  if (!isOnline) {
    return (
      <div className="additional-functions">
        <div className="offline-warning">
          <div className="offline-warning-header">
            <span className="offline-icon">⚠️</span>
            <h2>Dispositivo Offline</h2>
          </div>
          <p className="offline-message">
            El dispositivo <strong>"{deviceName}"</strong> no está disponible.
          </p>
          <p className="offline-submessage">
            Esto puede ocurrir si:
          </p>
          <ul>
            <li>La dirección IP o puerto cambió</li>
            <li>El dispositivo está apagado o desconectado de la red</li>
            <li>Hay un problema de conectividad</li>
          </ul>
          <div className="offline-actions">
            <button 
              className="btn btn-primary"
              onClick={() => {
                localStorage.setItem('lastSelectedDeviceId', deviceId.toString());
                navigate(`/devices/${deviceId}`);
              }}
            >
              📝 Editar Dispositivo
            </button>
            <button 
              className="btn btn-danger"
              onClick={() => {
                if (window.confirm(`¿Estás seguro de que deseas borrar el dispositivo "${deviceName}"?`)) {
                  // The delete will be handled in the device detail page
                  navigate(`/devices/${deviceId}`);
                }
              }}
            >
              🗑️ Borrar Dispositivo
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => checkDeviceStatus(deviceId)}
            >
              🔄 Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Command handlers
  const handleRestart = async () => {
    if (!window.confirm('¿Estás seguro de que deseas reiniciar el dispositivo?')) return;
    
    setProcessingCommand(true);
    try {
      const result = await restartDevice(deviceId);
      toast.success(result.message || 'Dispositivo reiniciado');
    } catch (error) {
      toast.error('Error al reiniciar el dispositivo');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handlePoweroff = async () => {
    if (!window.confirm('¿Deseas apagar el dispositivo? (Primera confirmación)')) return;
    if (!window.confirm('⚠️ SEGUNDA CONFIRMACIÓN: ¿Realmente deseas apagar el dispositivo?')) return;

    setProcessingCommand(true);
    try {
      const result = await poweroffDevice(deviceId);
      toast.success(result.message || 'Dispositivo apagado');
    } catch (error) {
      toast.error('Error al apagar el dispositivo');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handleSyncTime = async () => {
    setProcessingCommand(true);
    try {
      const result = await syncTime(deviceId);
      toast.success(result.message || 'Hora sincronizada');
    } catch (error) {
      toast.error('Error al sincronizar la hora');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handleTestVoice = async () => {
    setProcessingCommand(true);
    try {
      const result = await testVoice(deviceId, 0);
      toast.success(result.message || 'Prueba de voz completada');
    } catch (error) {
      toast.error('Error en la prueba de voz');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handleLoadMemory = async () => {
    setLoadingMemory(true);
    try {
      const result = await getMemoryInfo(deviceId);
      setMemoryInfo(result);
    } catch (error) {
      toast.error('Error al obtener información de memoria');
    } finally {
      setLoadingMemory(false);
    }
  };

  const handleClearAttendance = async () => {
    if (!window.confirm('¿Deseas limpiar todos los registros de asistencia?')) return;

    setProcessingCommand(true);
    try {
      await getRecentAttendance(deviceId, 0);
      toast.success('Registros de asistencia limpiados');
    } catch (error) {
      toast.error('Error al limpiar registros');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handleClearAllData = async () => {
    if (!window.confirm('⚠️ PRIMERA CONFIRMACIÓN: Esta acción eliminará TODOS los datos del dispositivo.')) return;
    if (!window.confirm('⚠️ SEGUNDA CONFIRMACIÓN: Usuarios, huellas, fotografías y registros se perderán.')) return;
    if (!window.confirm('⚠️ TERCERA CONFIRMACIÓN: ¿Está completamente seguro?')) return;

    setProcessingCommand(true);
    try {
      await clearAllData(deviceId);
      toast.success('Datos del dispositivo serán borrados en segundo plano');
    } catch (error) {
      toast.error('Error al borrar datos del dispositivo');
    } finally {
      setProcessingCommand(false);
    }
  };

  const handleLoadRecentLogs = async () => {
    setLoadingRecentLogs(true);
    try {
      const result = await getRecentAttendance(deviceId, 50);
      setRecentLogs(result.records || []);
    } catch (error) {
      toast.error('Error al obtener registros recientes');
    } finally {
      setLoadingRecentLogs(false);
    }
  };

  const handleLoadTemplates = async () => {
    setLoadingTemplates(true);
    try {
      const result = await getDeviceTemplates(deviceId);
      setTemplates(result);
    } catch (error) {
      toast.error('Error al obtener plantillas');
    } finally {
      setLoadingTemplates(false);
    }
  };

  return (
    <div className="additional-functions with-content">
      <div className="page-header">
        <h1>Funciones Adicionales: '{deviceName}'</h1>
        <button 
          className="btn btn-secondary"
          onClick={() => navigate(`/devices/${deviceId}`)}
        >
          Ver Detalles del Dispositivo
        </button>
      </div>

      <div className="functions-grid">
        {/* Restart */}
        <CommandCard
          icon="🔄"
          title="Reiniciar"
          description="Reinicia el dispositivo"
          action={handleRestart}
          loading={processingCommand}
        />

        {/* Poweroff */}
        <CommandCard
          icon="⏻️"
          title="Apagar"
          description="Apaga el dispositivo"
          action={handlePoweroff}
          variant="warning"
          loading={processingCommand}
          warning="Esta acción apagará el dispositivo"
        />

        {/* Sync Time */}
        <CommandCard
          icon="⏰"
          title="Sincronizar Hora"
          description="Sincroniza la hora del dispositivo"
          action={handleSyncTime}
          loading={processingCommand}
        />

        {/* Test Voice */}
        <CommandCard
          icon="🔊"
          title="Prueba de Voz"
          description="Reproduce un sonido de prueba"
          action={handleTestVoice}
          loading={processingCommand}
        />

        {/* Memory Info */}
        {memoryInfo ? (
          <MemoryCard memoryInfo={memoryInfo} onLoad={handleLoadMemory} loading={loadingMemory} />
        ) : (
          <CommandCard
            icon="📊"
            title="Información de Memoria"
            description="Ver capacidad de usuarios, huellas y registros"
            action={handleLoadMemory}
            loading={loadingMemory}
          />
        )}

        {/* Clear Attendance */}
        <CommandCard
          icon="🗑️"
          title="Limpiar Logs"
          description="Elimina registros de asistencia"
          action={handleClearAttendance}
          variant="warning"
          loading={processingCommand}
          warning="Se eliminarán todos los registros de asistencia"
        />

        {/* Clear All Data */}
        <CommandCard
          icon="💥"
          title="Borrar Todo"
          description="Borra todos los datos del dispositivo"
          action={handleClearAllData}
          variant="danger"
          loading={processingCommand}
          warning="PELIGRO: Elimina TODOS los datos incluyendo usuarios, huellas y registros"
        />

        {/* Recent Logs */}
        {recentLogs.length > 0 ? (
          <RecentLogsCard logs={recentLogs} onLoad={handleLoadRecentLogs} loading={loadingRecentLogs} />
        ) : (
          <CommandCard
            icon="📋"
            title="Registros Recientes"
            description="Últimos registros de asistencia"
            action={handleLoadRecentLogs}
            loading={loadingRecentLogs}
          />
        )}

        {/* Templates */}
        {templates ? (
          <TemplatesCard templates={templates} onLoad={handleLoadTemplates} loading={loadingTemplates} />
        ) : (
          <CommandCard
            icon="👆"
            title="Plantillas"
            description="Plantillas biométricas"
            action={handleLoadTemplates}
            loading={loadingTemplates}
          />
        )}
      </div>
    </div>
  );
}
