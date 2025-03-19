# Paweł Kędzierski 272400

import Pkg
Pkg.add("Plots")
using Plots

c::Vector{Float64} = [-2.0, -2.0, -2.0, -1.0, -1.0, -1.0, -1.0]
x::Vector{Float64} = [1.0, 2.0, 1.99999999999999, 1.0, -1.0, 0.75, 0.25]



function experiment(x::Float64, c::Float64)::Vector{Float64} 
    res::Vector{Float64} = Vector{Float64}()
    push!(res, x)

    for _ in 1:40
        x = x * x + c
        push!(res, x)
    end

    return res
end


function get_results()::Vector{Vector{Float64}}
    ret::Vector{Vector{Float64}}  = Vector{Vector{Float64}}()
    for i::Int64 in 1:7
        res::Vector{Float64} = experiment(x[i], c[i])
        push!(ret, res)
        println("\nResults for c = ", c[i], " and x = ", x[i])
        for n::Int64 in 1:41
            println(n - 1, " --- ", res[n])
        end
    end

    return ret
end

theme(:dark)  

vectors::Vector{Vector{Float64}} = get_results()

for i in 1:length(vectors)
    plot(title="Wykres dla eksperymentu $(i)", 
         xlabel="Iteracja", 
         ylabel="Wartość", 
         titlefont=14, 
         grid=:on, 
         legend=:bottomright)
    
    plot!(0:40, vectors[i], 
          label="x = $(x[i]), c = $(c[i])", 
          lw=2, 
          linecolor=:blue, 
          linestyle=:dash, 
          xlims=(0, 40), 
          ylims=(-10, 10))
    
    savefig("6_$(i)_plot.png")  # Zapisz jako SVG
end
