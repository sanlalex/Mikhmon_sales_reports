function App() {
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState(null);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Erreur lors du téléchargement du fichier');
            }

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    React.useEffect(() => {
        if (data) {
            // Daily Sales Chart
            const dailyCtx = document.getElementById('dailyChart');
            new Chart(dailyCtx, {
                type: 'line',
                data: {
                    labels: data.daily_sales.map(d => d.Date),
                    datasets: [{
                        label: 'Ventes Journalières (XOF)',
                        data: data.daily_sales.map(d => d.total),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });

            // Profile Distribution Chart
            const profileCtx = document.getElementById('profileChart');
            new Chart(profileCtx, {
                type: 'pie',
                data: {
                    labels: data.profile_stats.map(d => d.Profile),
                    datasets: [{
                        data: data.profile_stats.map(d => d.sum),
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)'
                        ]
                    }]
                }
            });

            // Hourly Distribution Chart
            const hourlyCtx = document.getElementById('hourlyChart');
            new Chart(hourlyCtx, {
                type: 'bar',
                data: {
                    labels: data.hourly_stats.map(d => `${d.Date}h`),
                    datasets: [{
                        label: 'Nombre de Transactions',
                        data: data.hourly_stats.map(d => d.Price),
                        backgroundColor: 'rgb(75, 192, 192)'
                    }]
                }
            });
        }
    }, [data]);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8 text-center">Analyse des Ventes</h1>
            
            <div className="mb-8">
                <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                />
            </div>

            {loading && (
                <div className="text-center py-4">
                    <p>Chargement en cours...</p>
                </div>
            )}

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            {data && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Ventes Journalières</h2>
                        <canvas id="dailyChart"></canvas>
                    </div>
                    
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Distribution par Forfait</h2>
                        <canvas id="profileChart"></canvas>
                    </div>
                    
                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Distribution Horaire</h2>
                        <canvas id="hourlyChart"></canvas>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Statistiques Globales</h2>
                        <div className="space-y-4">
                            <div>
                                <h3 className="font-medium">Total des ventes</h3>
                                <p className="text-2xl font-bold text-green-600">
                                    {data.daily_sales.reduce((acc, curr) => acc + curr.total, 0).toLocaleString()} XOF
                                </p>
                            </div>
                            <div>
                                <h3 className="font-medium">Nombre total de transactions</h3>
                                <p className="text-2xl font-bold text-blue-600">
                                    {data.daily_sales.reduce((acc, curr) => acc + curr.transactions, 0)}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
