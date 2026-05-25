const ChatApp = () => {
    const rootElement = document.getElementById('chat-root');
    const userId = parseInt(rootElement.dataset.userId);
    const username = rootElement.dataset.username;
    const csrfToken = rootElement.dataset.csrf;
    
    const [socket, setSocket] = React.useState(null);
    const [messages, setMessages] = React.useState([]);
    const [users, setUsers] = React.useState([]);
    const [inputText, setInputText] = React.useState('');
    const [privateTo, setPrivateTo] = React.useState(null);
    const [isBanned, setIsBanned] = React.useState(false);
    const [userRole, setUserRole] = React.useState('user');
    const [soundEnabled, setSoundEnabled] = React.useState(true);
    const [theme, setTheme] = React.useState('dark');
    const [showSettings, setShowSettings] = React.useState(false);
    const [showProfile, setShowProfile] = React.useState(null);
    
    const messagesEndRef = React.useRef(null);
    
    // Звуки
    const playSound = (type) => {
        if (!soundEnabled) return;
        const audio = new Audio();
        if (type === 'message') audio.src = '/static/chat/sounds/message.mp3';
        if (type === 'private') audio.src = '/static/chat/sounds/private.mp3';
        if (type === 'mention') audio.src = '/static/chat/sounds/mention.mp3';
        audio.volume = 0.3;
        audio.play().catch(e => console.log);
    };
    
    // Подключение к WebSocket
    React.useEffect(() => {
        // Получаем токен
        fetch('/chat/api/chat/token/', {
            headers: { 'X-CSRFToken': csrfToken }
        })
        .then(res => res.json())
        .then(data => {
            const newSocket = io('ws://localhost:8000/ws/chat/', {
                transports: ['websocket'],
                query: { token: data.token }
            });
            
            newSocket.on('connect', () => console.log('WebSocket connected'));
            newSocket.on('history', (data) => setMessages(data.messages));
            newSocket.on('message', (msg) => {
                setMessages(prev => [...prev, msg]);
                if (msg.user_id !== userId) playSound('message');
            });
            newSocket.on('private', (msg) => {
                setMessages(prev => [...prev, msg]);
                playSound('private');
            });
            newSocket.on('system', (msg) => setMessages(prev => [...prev, msg]));
            
            setSocket(newSocket);
        });
        
        // Загружаем пользователей
        fetch('/chat/api/chat/users/', {
            headers: { 'X-CSRFToken': csrfToken }
        })
        .then(res => res.json())
        .then(data => setUsers(data));
        
        // Загружаем настройки
        fetch('/chat/api/chat/settings/')
        .then(res => res.json())
        .then(data => {
            setSoundEnabled(data.sound_enabled);
            setTheme(data.theme);
            document.body.className = `theme-${data.theme}`;
        });
        
        // Получаем информацию о пользователе
        fetch('/chat/api/chat/user/')
        .then(res => res.json())
        .then(data => {
            setUserRole(data.role);
            setIsBanned(data.is_banned);
        });
        
        return () => socket?.close();
    }, []);
    
    const sendMessage = () => {
        if (!inputText.trim() || !socket || isBanned) return;
        
        if (privateTo) {
            socket.emit('private_message', {
                to_user_id: privateTo,
                text: inputText
            });
        } else {
            socket.emit('message', { text: inputText });
        }
        setInputText('');
    };
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
    
    React.useEffect(scrollToBottom, [messages]);
    
    const changeRole = (targetUserId, newRole) => {
        fetch('/chat/api/chat/change-role/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ user_id: targetUserId, role: newRole })
        }).then(() => {
            setUsers(users.map(u => 
                u.id === targetUserId ? { ...u, role: newRole, is_staff: newRole === 'admin' } : u
            ));
        });
    };
    
    const banUser = (targetUserId, targetUsername) => {
        const reason = prompt('Причина бана:');
        if (!reason) return;
        
        fetch('/chat/api/chat/ban/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ user_id: targetUserId, reason })
        }).then(() => {
            alert(`${targetUsername} забанен`);
            if (targetUserId === userId) setIsBanned(true);
        });
    };
    
    const unbanUser = (targetUserId) => {
        fetch('/chat/api/chat/unban/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ user_id: targetUserId })
        }).then(() => {
            alert('Пользователь разбанен');
            if (targetUserId === userId) setIsBanned(false);
        });
    };
    
    const updateSettings = (newSound, newTheme) => {
        fetch('/chat/api/chat/settings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ sound_enabled: newSound, theme: newTheme })
        });
        setSoundEnabled(newSound);
        setTheme(newTheme);
        document.body.className = `theme-${newTheme}`;
    };
    
    if (isBanned) {
        return (
            <div className="banned-page">
                <h2>⛔ Вы забанены ⛔</h2>
                <p>Вы не можете участвовать в чате.</p>
                <iframe src="https://edu.sravni.ru/kursy/info/kak-sozdat-chat-dlya-sajta/" width="100%" height="500" style={{border: 'none'}}></iframe>
            </div>
        );
    }
    
    const isAdmin = userRole === 'admin';
    const privateTarget = privateTo ? users.find(u => u.id === privateTo) : null;
    
    return (
        <div className={`chat-app theme-${theme}`}>
            {/* Левая панель — список пользователей */}
            <div className="chat-sidebar">
                <div className="sidebar-header">
                    <div className="online-title">📡 Онлайн ({users.length})</div>
                    <button className="settings-icon" onClick={() => setShowSettings(!showSettings)}>⚙️</button>
                </div>
                
                {/* Настройки */}
                {showSettings && (
                    <div className="settings-panel">
                        <label>
                            🔊 Звук:
                            <input type="checkbox" checked={soundEnabled} onChange={(e) => updateSettings(e.target.checked, theme)} />
                        </label>
                        <label>
                            🎨 Тема:
                            <select value={theme} onChange={(e) => updateSettings(soundEnabled, e.target.value)}>
                                <option value="dark">Тёмная</option>
                                <option value="light">Светлая</option>
                                <option value="gothic">Готическая</option>
                            </select>
                        </label>
                    </div>
                )}
                
                {/* Список пользователей */}
                <div className="user-list">
                    {users.map(user => (
                        <div key={user.id} className={`user-item ${privateTo === user.id ? 'active' : ''}`}>
                            <img src={user.avatar || '/static/default-avatar.png'} className="user-avatar" />
                            <div className="user-info" onClick={() => setShowProfile(user)}>
                                <div className="user-name">{user.username}</div>
                                <div className="user-role">{user.is_staff ? '👑 Админ' : '📜 Постоялец'}</div>
                            </div>
                            <div className="user-actions">
                                <button className="private-btn" onClick={() => setPrivateTo(privateTo === user.id ? null : user.id)} title="Написать в ЛС">
                                    💬
                                </button>
                                <button className="profile-btn" onClick={() => setShowProfile(user)} title="Профиль">
                                    👤
                                </button>
                                {isAdmin && user.id !== userId && (
                                    <>
                                        <select className="role-select" onChange={(e) => changeRole(user.id, e.target.value)} value={user.is_staff ? 'admin' : 'user'}>
                                            <option value="user">Пользователь</option>
                                            <option value="admin">Админ</option>
                                        </select>
                                        <button className="ban-btn" onClick={() => banUser(user.id, user.username)}>🚫</button>
                                        <button className="unban-btn" onClick={() => unbanUser(user.id)}>✅</button>
                                    </>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            
            {/* Центральная область — чат */}
            <div className="chat-main">
                <div className="chat-header">
                    <div className="chat-title">
                        {privateTo ? `💬 Приватный чат с ${privateTarget?.username}` : '💬 Общий чат'}
                    </div>
                    {privateTo && (
                        <button className="exit-private" onClick={() => setPrivateTo(null)}>
                            ✕ Выйти
                        </button>
                    )}
                    <button className="my-profile-btn" onClick={() => setShowProfile({ id: userId, username, role: userRole, is_staff: userRole === 'admin' })}>
                        👤 Мой профиль
                    </button>
                </div>
                
                <div className="messages-area">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`message ${msg.type === 'private' ? 'private' : ''} ${msg.type === 'system' ? 'system' : ''}`}>
                            {msg.type !== 'system' && (
                                <img src={msg.avatar || '/static/default-avatar.png'} className="message-avatar" onClick={() => setShowProfile({ id: msg.user_id, username: msg.username })} />
                            )}
                            <div className="message-bubble">
                                {msg.type !== 'system' && (
                                    <div className="message-header">
                                        <span className="message-username" onClick={() => setShowProfile({ id: msg.user_id, username: msg.username })}>
                                            {msg.username}
                                        </span>
                                        <span className="message-time">{new Date(msg.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                )}
                                <div className="message-text">{msg.text}</div>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                
                <div className="message-input-area">
                    <input 
                        type="text"
                        className="message-input"
                        placeholder={privateTo ? "💬 Введите приватное сообщение..." : "✏️ Введите сообщение..."}
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    />
                    <button className="send-button" onClick={sendMessage}>
                        📨
                    </button>
                </div>
            </div>
            
            {/* Модальное окно профиля */}
            {showProfile && (
                <div className="modal-overlay" onClick={() => setShowProfile(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <img src={showProfile.avatar || '/static/default-avatar.png'} className="modal-avatar" />
                        <h3>{showProfile.username}</h3>
                        <p>⭐ Роль: {showProfile.is_staff ? 'Администратор' : 'Пользователь'}</p>
                        <p>🆔 ID: {showProfile.id}</p>
                        <div className="modal-buttons">
                            <button className="modal-btn" onClick={() => {
                                setPrivateTo(showProfile.id);
                                setShowProfile(null);
                            }}>💬 Написать в ЛС</button>
                            <a href={`/profile/${showProfile.username}/`} target="_blank" className="modal-btn">📜 Анкеты</a>
                            <button className="modal-btn close-btn" onClick={() => setShowProfile(null)}>Закрыть</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// Рендер React-приложения
const rootElement = document.getElementById('chat-root');
if (rootElement) {
    ReactDOM.createRoot(rootElement).render(React.createElement(ChatApp));
}