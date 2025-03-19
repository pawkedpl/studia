# Pawel Kedzierski 272400
# parametry funkcji: typ zmiennoprzecinkowy T

function calc_macheps(T)
    macheps = one(T)
    while one(T) + macheps > one(T)
        macheps /= 2
    end
    return macheps * 2
end

function calculate_eta(T)
    eta = one(T)
    prev = eta

    while eta > zero(T)
        prev = eta
        eta /= 2
    end

    return prev
end

function calc_max(T)
    max = one(T)
    prev = max
    while !isinf(max)
        prev = max
        max *= 2
    end

    # szukam konkretnej wartosci
    dif = prev / 2
    while !isinf(prev + dif)
        prev += dif
        dif /= 2
    end

    return prev
end

println("Calculated macheps - values returned by eps")
println("For Float16 ", calc_macheps(Float16), " - ", eps(Float16))
println("For Float32 ", calc_macheps(Float32), " - ", eps(Float32))
println("For Float64 ", calc_macheps(Float64), " - ", eps(Float64))

println("\nCalculated eta - values returned by nextfloat")
println("For Float16 ", calculate_eta(Float16), " - ", nextfloat(Float16(0.0)))
println("For Float32 ", calculate_eta(Float32), " - ", nextfloat(Float32(0.0)))
println("For Float64 ", calculate_eta(Float64), " - ", nextfloat(Float64(0.0)))

println("\nValues returned by floatmin")
println("For Float32 ", floatmin(Float32))
println("For Float64 ", floatmin(Float64))

println("\nCalculated max - values returned by floatmax")
println("For Float16 ", calc_max(Float16), " - ", floatmax(Float16(0.0)))
println("For Float32 ", calc_max(Float32), " - ", floatmax(Float32(0.0)))
println("For Float64 ", calc_max(Float64), " - ", floatmax(Float64(0.0)))