# Pawel Kedzierski 272400
# parametry: typ zmiennoprzecinkowy

function kahan(T)
    result = T(3) * (T(4) / T(3) - one(T)) - one(T)

    return result
end

println("Kahan's macheps - values returned by eps")
println("For Float16 ", kahan(Float16), " - ", eps(Float16))
println("For Float32 ", kahan(Float32), " - ", eps(Float32))
println("For Float64 ", kahan(Float64), " - ", eps(Float64))