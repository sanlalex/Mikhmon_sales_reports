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
            const response = await fetch('/upload', {
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
            // Clear existing charts
            const charts = Chart.getChart('dailyChart');
            if (charts) charts.destroy();
            const profileCharts = Chart.getChart('profileChart');
            if (profileCharts) profileCharts.destroy();
            const hourlyCharts = Chart.getChart('hourlyChart');
            if (hourlyCharts) hourlyCharts.destroy();
            const ticketCharts = Chart.getChart('ticketDistributionChart');
            if (ticketCharts) ticketCharts.destroy();

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
                        data: data.profile_stats.map(d => d.total_sales),
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)'
                        ]
                    }]
                }
            });

            // Ticket Distribution Chart
            const ticketCtx = document.getElementById('ticketDistributionChart');
            new Chart(ticketCtx, {
                type: 'bar',
                data: {
                    labels: data.profile_stats.map(d => d.Profile),
                    datasets: [{
                        label: 'Nombre de Tickets Vendus',
                        data: data.profile_stats.map(d => d.tickets_sold),
                        backgroundColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)',
                            'rgb(255, 205, 86)'
                        ]
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
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
                        <h2 className="text-xl font-semibold mb-4">Ventes Selon les Heures</h2>
                        <canvas id="hourlyChart"></canvas>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Distribution des Tickets</h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Forfait
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Tickets Vendus
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Pourcentage
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Total Ventes
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {data.profile_stats.map((profile, index) => (
                                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {profile.Profile}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {profile.tickets_sold}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {profile.percentage}%
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {profile.total_sales.toLocaleString()} XOF
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Distribution des Tickets par Forfait</h2>
                        <canvas id="ticketDistributionChart"></canvas>
                    </div>

                    <div className="bg-white p-6 rounded-lg shadow">
                        <h2 className="text-xl font-semibold mb-4">Statistiques Globales</h2>
                        <div className="space-y-4">
                            <div>
                                <h3 className="font-medium">Total des ventes</h3>
                                <p className="text-2xl font-bold text-green-600">
                                    {data.profile_stats.reduce((acc, curr) => acc + curr.total_sales, 0).toLocaleString()} XOF
                                </p>
                            </div>
                            <div>
                                <h3 className="font-medium">Nombre total de tickets vendus</h3>
                                <p className="text-2xl font-bold text-blue-600">
                                    {data.profile_stats.reduce((acc, curr) => acc + curr.tickets_sold, 0)}
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
