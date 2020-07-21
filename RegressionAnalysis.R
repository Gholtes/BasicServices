setwd("/Users/grantholtes/Development/SpacialAnalysis/basicServices")

#Data files
files <- c("1kmMasterDataset.csv","2kmMasterDataset.csv","3kmMasterDataset.csv",
           "4kmMasterDataset.csv","5kmMasterDataset.csv","6kmMasterDataset.csv",
           "7kmMasterDataset.csv","8kmMasterDataset.csv","9kmMasterDataset.csv",
           "10kmMasterDataset.csv","11kmMasterDataset.csv","12kmMasterDataset.csv",
           "14kmMasterDataset.csv","16kmMasterDataset.csv","18kmMasterDataset.csv",
           "20kmMasterDataset.csv","22kmMasterDataset.csv","24kmMasterDataset.csv",
           "26kmMasterDataset.csv","28kmMasterDataset.csv","30kmMasterDataset.csv")
           "05kmMasterDataset.csv")

#Init array for results
results <- matrix(nrow = length(files)*4, ncol = 5,
                  dimnames = list(NULL, c("dataset", "radius", "type", "CoefficientOnIncome", "CoefficientOnIncome_P")))

rowNum = 1

#Iterate through datasets, each dataset is a specific radius
for (file in files){
  raw <- read.csv(file) #open file
  
  #Clean data by removing empty sa4
  raw <- subset(raw, raw$sa4name != "")
  
  #get radiu from filename
  kmRad = substr(file, start = 1, stop = 2)
  if (substr(kmRad,2,2)=="k"){kmRad = substr(file, start = 1, stop = 1)}
  if (kmRad == "05"){
    kmRad = 0.5
    }
  
  #Add columns as needed
  raw$medianIncomeTh <- raw$medianIncome / 1000
  
  #Service types to run regressions on
  typeNames <- c("bankCount", "healthCount", "schoolCount", "supermarketCount")
  typeCounts <- list(raw$bankCount, raw$healthCount, raw$schoolCount, raw$supermarketCount)
  
  for (i in 1:length(typeNames)){
    #get data for this service type only
    typeName <- typeNames[i]
    raw$typeCount <- raw[[typeName]]
    raw$lntypeCount <- log(raw[[typeName]])
    
    #define model as a poisson or log-linear model
    #% change in y for a unit change in Xi is 100*Bi, but should be estimated better as ratio of esimates due to error in approximations
    #As the % change is invarient to the intercept, we only need to store the coeffecient on income.
    
    #Poisson regression
    regPoss <- glm(typeCount ~ medianIncomeTh + sa4name + countPeople + distfromcenter + urban, family = "poisson", data = raw) #used as there are 0s in the dataset
   
    #Extract fitted coeff and P value
    incomeCoeff = regPoss$coefficients["medianIncomeTh"]
    incomeCoeffP = summary(regPoss)$coefficients[2,4]
    
    #record data:
    results[rowNum,] <- c(file, kmRad, typeName, incomeCoeff, incomeCoeffP)
    
    rowNum <- rowNum + 1
  }
}
#Save results
write.csv(results,"results.csv")

#format results to produce a line graph
res = as.data.frame(results[,1])
res$radius = as.numeric(results[,2])
res$type = results[,3]
res$coeff = as.numeric(results[,4])

res <- res[order(res$radius),]

delta = 19.2 #This is the average differnece between high and low income postcodes, in thousands of dollars

lims <- c(100*(exp(delta*min(res$coeff))-1),100*(exp(delta*max(res$coeff))-1))

#make plot
plot(res$radius[res$type == "bankCount"], 100*(exp(delta*res$coeff[res$type == "bankCount"])-1), type="b", pch = 16, lwd = 1,
     col = "red", 
     xlab = "Distance traveled (km)",
     ylab = "Difference in services (%)",
     ylim = lims)

points(res$radius[res$type == "supermarketCount"], 100*(exp(delta*res$coeff[res$type == "supermarketCount"])-1), col = "blue", type="b", pch = 16, lwd = 1)
points(res$radius[res$type == "schoolCount"], 100*(exp(delta*res$coeff[res$type == "schoolCount"])-1), col = "green", type="b", pch = 16, lwd = 1)
points(res$radius[res$type == "healthCount"], 100*(exp(delta*res$coeff[res$type == "healthCount"])-1), col = "purple", type="b", pch = 16, lwd = 1)
points(res$radius[res$type == "bankCount"], 100*(exp(delta*res$coeff[res$type == "bankCount"])-1), col = "red", type="b", pch = 16, lwd = 1)
lines(res$radius[res$type == "bankCount"], res$radius[res$type == "bankCount"]*0, col = "black", lwd = 1)


