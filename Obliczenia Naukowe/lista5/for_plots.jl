include("./blocksys.jl")
include("./IOMatrix.jl")
import Pkg
Pkg.add("LinearAlgebra")
Pkg.add("Plots")  # Dodanie Plots do generowania wykresów
using .blocksys, .IOMatrix
using LinearAlgebra, Base.Threads, Statistics
using Plots

sizes = [16, 10000, 50000, 100000, 300000, 500000]
gauss_times = Float64[]
gauss_mem = Float64[]
pivoted_times = Float64[]
pivoted_mem = Float64[]
lu_times = Float64[]
lu_mem = Float64[]
lu_pivoted_times = Float64[]
lu_pivoted_mem = Float64[]

function compare_all()
    for size in sizes
        A = IOMatrix.readMatrix("test_data/$(size)/A.txt")
        b = IOMatrix.readVector("test_data/$(size)/b.txt")
        Am, bm = deepcopy(A), deepcopy(b)

        # Pomiar czasu i pamięci dla algorytmów
        gauss = @timed blocksys.gauss(A, b)
        pivoted = @timed blocksys.gaussPivoted(deepcopy(A), deepcopy(b))
        lu_m = @timed blocksys.luSolve(deepcopy(A), deepcopy(b))
        lu_pivoted = @timed blocksys.luSolvePivoted(Am, bm)

        # Zbieranie wyników
        push!(gauss_times, gauss[2])
        push!(gauss_mem, gauss[3] / 2^20)
        push!(pivoted_times, pivoted[2])
        push!(pivoted_mem, pivoted[3] / 2^20)
        push!(lu_times, lu_m[2])
        push!(lu_mem, lu_m[3] / 2^20)
        push!(lu_pivoted_times, lu_pivoted[2])
        push!(lu_pivoted_mem, lu_pivoted[3] / 2^20)

        println("Size: $size | LU piv: $(lu_pivoted[2]) s | Mem: $(lu_pivoted[3] / 2^20) MB")
        println("----------------------------------------")
    end
end

function plot_results(sizes, gauss_times, pivoted_times, lu_times, lu_pivoted_times, 
                       gauss_mem, pivoted_mem, lu_mem, lu_pivoted_mem)
    # Wykres czasu
    plot(sizes, gauss_times, label="Gauss", xlabel="Rozmiar n", ylabel="Czas (s)", title="Czas działania algorytmu")
    plot!(sizes, pivoted_times, label="Gauss Pivoted")
    plot!(sizes, lu_times, label="LU")
    plot!(sizes, lu_pivoted_times, label="LU Pivoted")
    savefig("time_plot.png")

    # Wykres pamięci
    plot(sizes, gauss_mem, label="Gauss", xlabel="Rozmiar n", ylabel="Pamięć (MB)", title="Wykorzystana pamięć przez algorytm")
    plot!(sizes, pivoted_mem, label="Gauss Pivoted")
    plot!(sizes, lu_mem, label="LU")
    plot!(sizes, lu_pivoted_mem, label="LU Pivoted")
    savefig("memory_plot.png")
end

# Uruchomienie porównania algorytmów i generowanie wykresów
compare_all()
plot_results(sizes, gauss_times, pivoted_times, lu_times, lu_pivoted_times, 
              gauss_mem, pivoted_mem, lu_mem, lu_pivoted_mem)
